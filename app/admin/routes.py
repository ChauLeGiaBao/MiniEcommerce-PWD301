from datetime import date
from functools import wraps
from flask import abort, flash, g, redirect, render_template, request, session, url_for
from flask_login import current_user
from sqlalchemy import cast, func, or_, String
from sqlalchemy.exc import IntegrityError

from app.admin import admin_bp
from app.extensions import db, login_manager
from app.models import ChiTietDonHang, DanhMuc, DonHang, SanPham, User

# Bổ sung các phương thức tương thích UserMixin cho User model nếu chưa có,
# giúp Flask-Login hoạt động hoàn hảo mà không cần sửa file app/models/nguoi_dung.py
if not hasattr(User, "get_id"):
    User.get_id = lambda self: str(self.MANGUOIDUNG)
if not hasattr(User, "is_authenticated"):
    User.is_authenticated = property(lambda self: True)
if not hasattr(User, "is_active"):
    User.is_active = property(lambda self: getattr(self, "TRANGTHAIND", 1) == 1)
if not hasattr(User, "is_anonymous"):
    User.is_anonymous = property(lambda self: False)


def _load_user_by_id(user_id):
    """Flask-Login user loader nạp User theo khóa chính MANGUOIDUNG."""
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError, Exception):
        return None


login_manager.user_loader(_load_user_by_id)


@admin_bp.record
def on_admin_init(state):
    """Đăng ký user loader mỗi khi admin_bp được mount vào một Flask app."""
    login_manager.user_loader(_load_user_by_id)


@admin_bp.teardown_app_request
def cleanup_login_user(exc=None):
    """Đảm bảo g không giữ vết user đã đăng xuất giữa các request trong cùng app context."""
    if hasattr(g, "_login_user"):
        del g._login_user


# Ngưỡng số lượng tồn kho thấp thống nhất cho toàn hệ thống
LOW_STOCK_THRESHOLD = 5

# Danh mục trạng thái đơn hàng hợp lệ hỗ trợ bởi schema
VALID_ORDER_STATUSES = {
    0: "Mới / Chờ xử lý",
    1: "Đang xử lý",
    2: "Hoàn thành",
    3: "Đã hủy",
}


# ==============================================================================
# Helper Xác Thực & Phân Quyền RBAC (Bảo vệ toàn bộ /admin/*)
# ==============================================================================
def get_current_user():
    """
    Lấy thông tin user hiện tại duy nhất từ Flask-Login current_user.
    Tuân thủ LO01: Không đọc session['role'], session['user_id'] hay g.user để tự cấp quyền.
    """
    if current_user and getattr(current_user, "is_authenticated", False):
        return current_user
    return None


def get_user_role(user):
    """Lấy role chuẩn hóa của user (chữ thường, loại bỏ khoảng trắng)."""
    if not user:
        return ""
    role_val = getattr(user, "ROLE", None) or getattr(user, "role", None) or ""
    return str(role_val).strip().lower()


def is_admin(user):
    """Kiểm tra xem user có quyền Admin hay không (ROLE == 'admin')."""
    return get_user_role(user) == "admin"


def is_staff(user):
    """Kiểm tra xem user có quyền Staff hay không (ROLE == 'staff')."""
    return get_user_role(user) == "staff"


def admin_required(f):
    """Decorator kiểm tra quyền Admin cho từng route cụ thể nếu cần."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return {"error": "Unauthorized", "message": "Vui lòng đăng nhập để tiếp tục."}, 401
            flash("Vui lòng đăng nhập để truy cập trang quản trị.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if not is_admin(user):
            abort(403)
        g.admin_user = user
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.before_request
def require_admin_or_staff():
    """
    Bảo vệ toàn bộ các endpoint thuộc /admin/* theo ma trận RBAC:
    - Guest (chưa đăng nhập qua Flask-Login): Chuyển hướng về /auth/login (hoặc 401 nếu ajax).
    - Customer: Chặn 403 Forbidden với mọi route /admin/*.
    - Staff: Được phép truy cập Dashboard và xem/cập nhật Đơn hàng;
             BỊ CHẶN 403 Forbidden đối với Quản lý Sản phẩm (Product CRUD).
    - Admin: Toàn quyền truy cập tất cả các endpoint.
    - Tuyệt đối không nhận session['role'] giả mạo.
    """
    user = get_current_user()
    if not user:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"error": "Unauthorized", "message": "Vui lòng đăng nhập để truy cập trang quản trị."}, 401
        flash("Vui lòng đăng nhập để truy cập trang quản trị.", "warning")
        return redirect(url_for("auth.login", next=request.url))

    role = get_user_role(user)

    if role == "admin":
        g.admin_user = user
        return

    if role == "staff":
        # Staff chỉ được xem dashboard và quản lý orders (xem list, detail, đổi status)
        # Chặn staff truy cập Product CRUD
        endpoint = request.endpoint or ""
        if "product" in endpoint:
            abort(403)
        g.admin_user = user
        return

    # User có role khác (customer, ...) -> 403 Forbidden
    abort(403)


# ==============================================================================
# 1. Admin Dashboard
# ==============================================================================
@admin_bp.route("/")
def dashboard():
    """
    Trang tổng quan Admin:
    - Tổng số sản phẩm
    - Tổng số đơn hàng & tổng doanh thu
    - Phân loại đơn hàng theo trạng thái
    - Cảnh báo sản phẩm sắp hết hàng (SOLUONGTON <= LOW_STOCK_THRESHOLD)
    - Danh sách đơn hàng mới gần đây
    - Tất cả dữ liệu query từ DB thật, không hard-code.
    """
    product_count = SanPham.query.count()
    order_count = DonHang.query.count()
    low_stock_count = SanPham.query.filter(SanPham.SOLUONGTON <= LOW_STOCK_THRESHOLD).count()

    # Thống kê doanh thu (an toàn khi DB chưa có order, scalar trả về None -> 0)
    # Tuân thủ LO02: Định nghĩa rõ ràng cách tính doanh thu:
    # - total_revenue: Tổng doanh thu từ các đơn hàng hợp lệ (loại trừ đơn đã hủy TRANGTHAI == 3)
    # - completed_revenue: Doanh thu thực thu từ các đơn đã hoàn thành (TRANGTHAI == 2)
    total_revenue = (
        db.session.query(func.coalesce(func.sum(DonHang.TONGGIATRI), 0))
        .filter(DonHang.TRANGTHAI != 3)
        .scalar()
        or 0
    )
    completed_revenue = (
        db.session.query(func.coalesce(func.sum(DonHang.TONGGIATRI), 0))
        .filter(DonHang.TRANGTHAI == 2)
        .scalar()
        or 0
    )

    # Phân loại trạng thái đơn hàng
    pending_count = DonHang.query.filter_by(TRANGTHAI=0).count()
    processing_count = DonHang.query.filter_by(TRANGTHAI=1).count()
    completed_count = DonHang.query.filter_by(TRANGTHAI=2).count()
    cancelled_count = DonHang.query.filter_by(TRANGTHAI=3).count()

    # 5 đơn hàng gần nhất
    recent_orders = DonHang.query.order_by(DonHang.MADONHANG.desc()).limit(5).all()

    # Danh sách sản phẩm sắp hết hàng
    low_stock_products = (
        SanPham.query.filter(SanPham.SOLUONGTON <= LOW_STOCK_THRESHOLD)
        .order_by(SanPham.SOLUONGTON.asc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin_dashboard.html",
        product_count=product_count,
        order_count=order_count,
        low_stock_count=low_stock_count,
        low_stock_threshold=LOW_STOCK_THRESHOLD,
        total_revenue=total_revenue,
        completed_revenue=completed_revenue,
        pending_count=pending_count,
        processing_count=processing_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products,
        valid_statuses=VALID_ORDER_STATUSES,
    )


# ==============================================================================
# 2. Product Admin Nâng Cao (Quản lý sản phẩm)
# ==============================================================================
@admin_bp.route("/products", methods=["GET", "POST"])
def products():
    """
    Quản lý sản phẩm Admin:
    - Search theo tên sản phẩm (q)
    - Filter category (category_id)
    - Filter low stock (low_stock: '1' hoặc 'out')
    - Pagination và bảo lưu query parameters
    - Validation giá và tồn kho không chấp nhận số âm
    """
    categories = DanhMuc.query.order_by(DanhMuc.TENDM).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_raw = request.form.get("price", "").strip()
        stock_raw = request.form.get("stock", "0").strip()
        status_raw = request.form.get("status", "1").strip()
        category_id_raw = request.form.get("category_id", "").strip()
        image = request.form.get("image", "").strip() or None
        description = request.form.get("description", "").strip() or None

        errors = []

        # Validate tên sản phẩm
        if not name:
            errors.append("Tên sản phẩm không được để trống.")
        elif len(name) > 200:
            errors.append("Tên sản phẩm không được vượt quá 200 ký tự.")

        # Validate giá sản phẩm (không chấp nhận số âm)
        price = None
        try:
            price = float(price_raw)
            if price < 0:
                errors.append("Giá sản phẩm phải lớn hơn hoặc bằng 0.")
        except (TypeError, ValueError):
            errors.append("Giá sản phẩm phải là số hợp lệ.")

        # Validate tồn kho (không chấp nhận số âm)
        stock = 0
        try:
            stock = int(stock_raw) if stock_raw else 0
            if stock < 0:
                errors.append("Số lượng tồn kho phải lớn hơn hoặc bằng 0.")
        except (TypeError, ValueError):
            errors.append("Số lượng tồn kho phải là số nguyên không âm.")

        # Validate trạng thái (0: Tạm ẩn, 1: Đang bán)
        status = 1
        try:
            status = int(status_raw)
            if status not in (0, 1):
                errors.append("Trạng thái sản phẩm không hợp lệ (chỉ nhận 0 hoặc 1).")
        except (TypeError, ValueError):
            errors.append("Trạng thái sản phẩm không hợp lệ.")

        # Validate danh mục
        category_id = None
        if category_id_raw:
            try:
                cat_val = int(category_id_raw)
                if cat_val > 0:
                    if db.session.get(DanhMuc, cat_val):
                        category_id = cat_val
                    else:
                        errors.append("Danh mục đã chọn không tồn tại trong hệ thống.")
            except (TypeError, ValueError):
                errors.append("Mã danh mục không hợp lệ.")

        # Validate độ dài chuỗi
        if image and len(image) > 500:
            errors.append("Đường dẫn hình ảnh không được vượt quá 500 ký tự.")
        if description and len(description) > 500:
            errors.append("Mô tả sản phẩm không được vượt quá 500 ký tự.")

        if errors:
            for err in errors:
                flash(err, "danger")
            # Trả về trang kèm danh sách sản phẩm trang 1 và bảo lưu form_data
            query = SanPham.query.order_by(SanPham.MASANPHAM.desc())
            pagination = query.paginate(page=1, per_page=10, error_out=False)
            return render_template(
                "admin_products.html",
                products=pagination.items,
                pagination=pagination,
                categories=categories,
                q="",
                category_id="",
                low_stock="",
                low_stock_threshold=LOW_STOCK_THRESHOLD,
                form_data=request.form,
            )
        else:
            product = SanPham(
                TENSPH=name,
                HINHANH=image,
                DONGIA=price,
                MOTA=description,
                SOLUONGTON=stock,
                TRANGTHAISPH=status,
                MADANHMUC=category_id,
            )
            db.session.add(product)
            db.session.commit()
            flash(f"Đã thêm sản phẩm '{name}' thành công.", "success")
            return redirect(url_for("admin.products"))

    # Xử lý GET: Search, Filter, Pagination
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", "").strip()
    low_stock = request.args.get("low_stock", "").strip()
    page = request.args.get("page", 1, type=int)

    query = SanPham.query

    # 1. Search theo tên sản phẩm
    if q:
        query = query.filter(SanPham.TENSPH.ilike(f"%{q}%"))

    # 2. Filter theo danh mục
    if category_id:
        try:
            cat_id_int = int(category_id)
            if cat_id_int > 0:
                query = query.filter(SanPham.MADANHMUC == cat_id_int)
        except (ValueError, TypeError):
            pass

    # 3. Filter theo tồn kho
    if low_stock == "1" or low_stock.lower() == "low":
        query = query.filter(SanPham.SOLUONGTON <= LOW_STOCK_THRESHOLD)
    elif low_stock == "out":
        query = query.filter(SanPham.SOLUONGTON == 0)

    # 4. Sắp xếp mới nhất và phân trang
    query = query.order_by(SanPham.MASANPHAM.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "admin_products.html",
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        q=q,
        category_id=category_id,
        low_stock=low_stock,
        low_stock_threshold=LOW_STOCK_THRESHOLD,
    )


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    """
    Chỉnh sửa sản phẩm hiện có:
    Validate đầy đủ: tên, giá, tồn kho, danh mục, trạng thái (không chấp nhận số âm).
    """
    product = db.get_or_404(SanPham, product_id)
    categories = DanhMuc.query.order_by(DanhMuc.TENDM).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_raw = request.form.get("price", "").strip()
        stock_raw = request.form.get("stock", "0").strip()
        status_raw = request.form.get("status", "1").strip()
        category_id_raw = request.form.get("category_id", "").strip()
        image = request.form.get("image", "").strip() or None
        description = request.form.get("description", "").strip() or None

        errors = []

        if not name:
            errors.append("Tên sản phẩm không được để trống.")
        elif len(name) > 200:
            errors.append("Tên sản phẩm không được vượt quá 200 ký tự.")

        price = None
        try:
            price = float(price_raw)
            if price < 0:
                errors.append("Giá sản phẩm phải lớn hơn hoặc bằng 0.")
        except (TypeError, ValueError):
            errors.append("Giá sản phẩm phải là số hợp lệ.")

        stock = 0
        try:
            stock = int(stock_raw) if stock_raw else 0
            if stock < 0:
                errors.append("Số lượng tồn kho phải lớn hơn hoặc bằng 0.")
        except (TypeError, ValueError):
            errors.append("Số lượng tồn kho phải là số nguyên không âm.")

        status = 1
        try:
            status = int(status_raw)
            if status not in (0, 1):
                errors.append("Trạng thái sản phẩm không hợp lệ (chỉ nhận 0 hoặc 1).")
        except (TypeError, ValueError):
            errors.append("Trạng thái sản phẩm không hợp lệ.")

        category_id = None
        if category_id_raw:
            try:
                cat_val = int(category_id_raw)
                if cat_val > 0:
                    if db.session.get(DanhMuc, cat_val):
                        category_id = cat_val
                    else:
                        errors.append("Danh mục đã chọn không tồn tại trong hệ thống.")
            except (TypeError, ValueError):
                errors.append("Mã danh mục không hợp lệ.")

        if image and len(image) > 500:
            errors.append("Đường dẫn hình ảnh không được vượt quá 500 ký tự.")
        if description and len(description) > 500:
            errors.append("Mô tả sản phẩm không được vượt quá 500 ký tự.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "admin_product_form.html",
                product=product,
                categories=categories,
                form_data=request.form,
            )
        else:
            product.TENSPH = name
            product.HINHANH = image
            product.DONGIA = price
            product.MOTA = description
            product.SOLUONGTON = stock
            product.TRANGTHAISPH = status
            product.MADANHMUC = category_id
            db.session.commit()
            flash(f"Đã cập nhật sản phẩm #{product.MASANPHAM} '{product.TENSPH}' thành công.", "success")
            return redirect(url_for("admin.products"))

    return render_template(
        "admin_product_form.html",
        product=product,
        categories=categories,
    )


@admin_bp.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    """
    Xóa an toàn:
    - Sản phẩm đã nằm trong đơn hàng (ChiTietDonHang) không được xóa gây lỗi FK.
    - Hiển thị thông báo nghiệp vụ rõ ràng, gợi ý chuyển trạng thái sang Tạm ẩn.
    """
    product = db.get_or_404(SanPham, product_id)

    in_order = ChiTietDonHang.query.filter_by(MASANPHAM=product_id).first()
    if in_order:
        flash(
            f"Không thể xóa sản phẩm '#{product.MASANPHAM} - {product.TENSPH}' vì đã có trong đơn hàng tham chiếu. "
            "Bạn có thể chuyển trạng thái sang 'Tạm ẩn' nếu muốn ngừng kinh doanh mà không làm mất lịch sử đơn hàng.",
            "warning",
        )
        return redirect(url_for("admin.products"))

    try:
        product_name = product.TENSPH
        db.session.delete(product)
        db.session.commit()
        flash(f"Đã xóa sản phẩm '{product_name}' thành công.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Không thể xóa sản phẩm #{product_id} do ràng buộc dữ liệu khóa ngoại.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Đã xảy ra lỗi khi xóa sản phẩm: {e}", "danger")

    return redirect(url_for("admin.products"))


# ==============================================================================
# 3. Order Admin Nâng Cao (Quản lý đơn hàng)
# ==============================================================================
@admin_bp.route("/orders")
def orders():
    """
    Danh sách đơn đặt hàng nâng cao:
    - Search theo mã đơn / người nhận / SĐT
    - Filter theo trạng thái đơn hàng
    - Sort mới nhất / cũ nhất
    - Pagination và giữ toàn bộ query parameters khi đổi trang
    """
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    sort = request.args.get("sort", "newest").strip()
    page = request.args.get("page", 1, type=int)

    query = DonHang.query

    # 1. Search theo mã đơn / người nhận / SĐT
    if q:
        or_clauses = [
            DonHang.HOTENNHAN.ilike(f"%{q}%"),
            DonHang.SDTNHAN.ilike(f"%{q}%"),
        ]
        if q.isdigit():
            or_clauses.append(DonHang.MADONHANG == int(q))
        elif q.startswith("#") and q[1:].isdigit():
            or_clauses.append(DonHang.MADONHANG == int(q[1:]))
        else:
            or_clauses.append(cast(DonHang.MADONHANG, String).ilike(f"%{q}%"))
        query = query.filter(or_(*or_clauses))

    # 2. Filter theo trạng thái
    if status != "":
        try:
            st_int = int(status)
            if st_int in VALID_ORDER_STATUSES:
                query = query.filter(DonHang.TRANGTHAI == st_int)
        except (ValueError, TypeError):
            pass

    # 3. Sort mới nhất / cũ nhất
    if sort == "oldest":
        query = query.order_by(DonHang.MADONHANG.asc())
    else:
        query = query.order_by(DonHang.MADONHANG.desc())

    # 4. Phân trang
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "admin_orders.html",
        orders=pagination.items,
        pagination=pagination,
        valid_statuses=VALID_ORDER_STATUSES,
        q=q,
        status=status,
        sort=sort,
    )


@admin_bp.route("/orders/<int:order_id>")
def order_detail(order_id):
    """
    Trang chi tiết đơn hàng:
    - Danh sách chi tiết các mặt hàng (tên, đơn giá, số lượng, subtotal)
    - Thông tin người nhận, điện thoại, địa chỉ giao hàng, ngày đặt
    - Tổng tiền và form cập nhật trạng thái đơn hàng
    """
    order = db.get_or_404(DonHang, order_id)
    return render_template(
        "admin_order_detail.html",
        order=order,
        valid_statuses=VALID_ORDER_STATUSES,
    )


@admin_bp.post("/orders/<int:order_id>/status")
def update_order_status(order_id):
    """
    Cập nhật trạng thái đơn hàng:
    - Chỉ nhận các status hợp lệ (0, 1, 2, 3)
    - Không nhận status tùy ý từ request/client
    - Thông báo success/error rõ ràng
    - Không tự thêm cột DB nếu model hiện tại chưa hỗ trợ
    """
    status_raw = request.form.get("status")
    try:
        if status_raw is None or status_raw.strip() == "":
            raise ValueError("Thiếu trạng thái")
        status = int(status_raw)
        if status not in VALID_ORDER_STATUSES:
            raise ValueError("Trạng thái không hợp lệ")
    except (TypeError, ValueError):
        flash("Trạng thái đơn hàng không hợp lệ (hệ thống chỉ chấp nhận từ 0 đến 3).", "danger")
        return redirect(request.referrer or url_for("admin.orders"))

    order = db.get_or_404(DonHang, order_id)
    order.TRANGTHAI = status
    db.session.commit()
    flash(
        f"Đã cập nhật trạng thái đơn hàng #{order.MADONHANG} thành '{VALID_ORDER_STATUSES[status]}'.",
        "success",
    )
    return redirect(request.referrer or url_for("admin.orders"))