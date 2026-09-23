from flask import flash, redirect, render_template, request, url_for

from app.admin import admin_bp
from app.extensions import db
from app.models import ChiTietDonHang, DonHang, SanPham

# ==============================================================================
# TODO: Tích hợp xác thực Admin khi hoàn thành module Auth (Kiên / Bảo).
# Sau này cần bổ sung @login_required và @admin_required (kiểm tra current_user.ROLE == 'admin')
# cho tất cả các route bên dưới để bảo vệ khu vực quản trị.
# ==============================================================================

VALID_ORDER_STATUSES = {0, 1, 2, 3}


# TODO: Thêm @login_required, @admin_required
@admin_bp.route("/")
def dashboard():
    return render_template(
        "admin_dashboard.html",
        product_count=SanPham.query.count(),
        order_count=DonHang.query.count(),
        low_stock_count=SanPham.query.filter(SanPham.SOLUONGTON <= 5).count(),
    )


# TODO: Thêm @login_required, @admin_required
@admin_bp.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", type=float)
        stock = request.form.get("stock", type=int)
        if stock is None:
            stock = 0

        status_val = request.form.get("status", type=int)
        status = status_val if status_val in (0, 1) else 1

        category_id = request.form.get("category_id", type=int)
        if category_id is not None and category_id <= 0:
            category_id = None

        if not name:
            flash("Tên sản phẩm không được để trống.", "danger")
        elif price is None or price < 0:
            flash("Giá sản phẩm phải lớn hơn hoặc bằng 0.", "danger")
        elif stock < 0:
            flash("Số lượng tồn kho không được âm.", "danger")
        else:
            product = SanPham(
                TENSPH=name,
                HINHANH=request.form.get("image", "").strip() or None,
                DONGIA=price,
                MOTA=request.form.get("description", "").strip() or None,
                SOLUONGTON=stock,
                TRANGTHAISPH=status,
                MADANHMUC=category_id,
            )
            db.session.add(product)
            db.session.commit()
            flash("Đã thêm sản phẩm.", "success")
            return redirect(url_for("admin.products"))

    return render_template("admin_products.html", products=SanPham.query.order_by(SanPham.MASANPHAM.desc()).all())


# TODO: Thêm @login_required, @admin_required
@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = SanPham.query.get_or_404(product_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", type=float)
        stock = request.form.get("stock", type=int)
        if stock is None:
            stock = 0

        status_val = request.form.get("status", type=int)
        status = status_val if status_val in (0, 1) else 1

        category_id = request.form.get("category_id", type=int)
        if category_id is not None and category_id <= 0:
            category_id = None

        if not name:
            flash("Tên sản phẩm không được để trống.", "danger")
        elif price is None or price < 0:
            flash("Giá sản phẩm phải lớn hơn hoặc bằng 0.", "danger")
        elif stock < 0:
            flash("Số lượng tồn kho không được âm.", "danger")
        else:
            product.TENSPH = name
            product.HINHANH = request.form.get("image", "").strip() or None
            product.DONGIA = price
            product.MOTA = request.form.get("description", "").strip() or None
            product.SOLUONGTON = stock
            product.TRANGTHAISPH = status
            product.MADANHMUC = category_id
            db.session.commit()
            flash("Đã cập nhật sản phẩm.", "success")
            return redirect(url_for("admin.products"))

    return render_template("admin_product_form.html", product=product)


# TODO: Thêm @login_required, @admin_required
@admin_bp.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    product = SanPham.query.get_or_404(product_id)
    if ChiTietDonHang.query.filter_by(MASANPHAM=product_id).first():
        flash("Không thể xóa sản phẩm đã có trong đơn hàng.", "warning")
    else:
        db.session.delete(product)
        db.session.commit()
        flash("Đã xóa sản phẩm.", "success")
    return redirect(url_for("admin.products"))


# TODO: Thêm @login_required, @admin_required
@admin_bp.route("/orders")
def orders():
    orders = DonHang.query.order_by(DonHang.MADONHANG.desc()).all()
    return render_template("admin_orders.html", orders=orders)


# TODO: Thêm @login_required, @admin_required
@admin_bp.post("/orders/<int:order_id>/status")
def update_order_status(order_id):
    status = request.form.get("status", type=int)
    if status not in VALID_ORDER_STATUSES:
        flash("Trạng thái đơn hàng không hợp lệ.", "danger")
        return redirect(url_for("admin.orders"))

    order = DonHang.query.get_or_404(order_id)
    order.TRANGTHAI = status
    db.session.commit()
    flash("Đã cập nhật trạng thái đơn hàng.", "success")
    return redirect(url_for("admin.orders"))