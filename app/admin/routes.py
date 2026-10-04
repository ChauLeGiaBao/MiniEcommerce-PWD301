from datetime import date
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.admin import admin_bp
from app.extensions import db
from app.models import ChiTietDonHang, DanhMuc, DonHang, SanPham, User

# ==============================================================================
# TODO: Tích hợp xác thực Admin khi hoàn thành module Auth (Kiên / Bảo).
# Sau này cần bổ sung @login_required và @admin_required (kiểm tra current_user.ROLE == 'admin')
# cho tất cả các route bên dưới để bảo vệ khu vực quản trị.
# ==============================================================================

# Ngưỡng số lượng tồn kho thấp thống nhất cho toàn hệ thống
LOW_STOCK_THRESHOLD = 5

# Danh mục trạng thái đơn hàng hợp lệ hỗ trợ bởi schema Kiên
VALID_ORDER_STATUSES = {
    0: "Mới / Chờ xử lý",
    1: "Đang xử lý",
    2: "Hoàn thành",
    3: "Đã hủy",
}


# ==============================================================================
# 1. Admin Dashboard
# ==============================================================================
@admin_bp.route("/")
def dashboard():
    """
    Trang tổng quan Admin:
    - Tổng số sản phẩm
    - Số sản phẩm tồn kho thấp (SOLUONGTON <= LOW_STOCK_THRESHOLD)
    - Tổng số đơn hàng & thống kê trạng thái, tổng doanh thu
    - Hoạt động an toàn, không bị crash khi database chưa có order
    """
    product_count = SanPham.query.count()
    order_count = DonHang.query.count()
    low_stock_count = SanPham.query.filter(SanPham.SOLUONGTON <= LOW_STOCK_THRESHOLD).count()

    # Thống kê doanh thu (an toàn khi chưa có order, scalar trả về None -> 0)
    total_revenue = db.session.query(func.sum(DonHang.TONGGIATRI)).scalar() or 0

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
        pending_count=pending_count,
        processing_count=processing_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products,
        valid_statuses=VALID_ORDER_STATUSES,
    )


# ==============================================================================
# 2. Product Admin (Quản lý sản phẩm)
# ==============================================================================
@admin_bp.route("/products", methods=["GET", "POST"])
def products():
    """
    Danh sách sản phẩm từ database và Form thêm sản phẩm mới.
    Validate đầy đủ: tên, giá, tồn kho, danh mục, trạng thái.
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

        # Validate giá sản phẩm
        price = None
        try:
            price = float(price_raw)
            if price < 0:
                errors.append("Giá sản phẩm phải lớn hơn hoặc bằng 0.")
        except (TypeError, ValueError):
            errors.append("Giá sản phẩm phải là số hợp lệ.")

        # Validate tồn kho
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

    all_products = SanPham.query.order_by(SanPham.MASANPHAM.desc()).all()
    return render_template(
        "admin_products.html",
        products=all_products,
        categories=categories,
        low_stock_threshold=LOW_STOCK_THRESHOLD,
    )


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    """
    Chỉnh sửa sản phẩm hiện có.
    Validate đầy đủ: tên, giá, tồn kho, danh mục, trạng thái.
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
    Xóa sản phẩm với xử lý an toàn:
    Nếu sản phẩm đã từng được đặt trong bất kỳ đơn hàng nào (ChiTietDonHang),
    ngăn chặn xóa để bảo toàn lịch sử đơn hàng và thông báo hướng dẫn tạm ẩn sản phẩm.
    """
    product = db.get_or_404(SanPham, product_id)

    in_order = ChiTietDonHang.query.filter_by(MASANPHAM=product_id).first()
    if in_order:
        flash(
            f"Không thể xóa sản phẩm '#{product.MASANPHAM} - {product.TENSPH}' vì đã có trong đơn hàng tham chiếu. "
            "Bạn có thể chuyển trạng thái sang 'Tạm ẩn' nếu muốn ngừng kinh doanh.",
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
# 3. Order Admin (Quản lý đơn hàng)
# ==============================================================================
@admin_bp.route("/orders")
def orders():
    """
    Danh sách tất cả các đơn hàng:
    Hiển thị mã đơn, người nhận/khách hàng, thời gian đặt, tổng tiền, trạng thái.
    """
    all_orders = DonHang.query.order_by(DonHang.MADONHANG.desc()).all()
    return render_template(
        "admin_orders.html",
        orders=all_orders,
        valid_statuses=VALID_ORDER_STATUSES,
    )


@admin_bp.route("/orders/<int:order_id>")
def order_detail(order_id):
    """
    Trang chi tiết đơn hàng:
    - Danh sách chi tiết các mặt hàng (tên, hình ảnh, đơn giá, số lượng, subtotal)
    - Thông tin người nhận, điện thoại, địa chỉ giao hàng
    - Tổng tiền và cập nhật trạng thái đơn hàng
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
    Cập nhật trạng thái đơn hàng theo các giá trị schema Kiên hỗ trợ (0, 1, 2, 3).
    Lưu lại database thật và chuyển hướng về trang trước (order list hoặc order detail).
    """
    status_raw = request.form.get("status")
    try:
        status = int(status_raw)
        if status not in VALID_ORDER_STATUSES:
            raise ValueError
    except (TypeError, ValueError):
        flash("Trạng thái đơn hàng không hợp lệ (chỉ nhận từ 0 đến 3).", "danger")
        return redirect(request.referrer or url_for("admin.orders"))

    order = db.get_or_404(DonHang, order_id)
    order.TRANGTHAI = status
    db.session.commit()
    flash(
        f"Đã cập nhật trạng thái đơn hàng #{order.MADONHANG} thành '{VALID_ORDER_STATUSES[status]}'.",
        "success",
    )
    return redirect(request.referrer or url_for("admin.orders"))