from datetime import date

from flask import flash, redirect, render_template, request, url_for

from app.admin import admin_bp
from app.extensions import db
from app.models import ChiTietDonHang, DonHang, SanPham


@admin_bp.route("/")
def dashboard():
    return render_template(
        "admin_dashboard.html",
        product_count=SanPham.query.count(),
        order_count=DonHang.query.count(),
        low_stock_count=SanPham.query.filter(SanPham.SOLUONGTON <= 5).count(),
    )


@admin_bp.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        product = SanPham(
            TENSPH=request.form.get("name", "").strip(),
            HINHANH=request.form.get("image", "").strip() or None,
            DONGIA=request.form.get("price", type=float),
            MOTA=request.form.get("description", "").strip() or None,
            SOLUONGTON=request.form.get("stock", type=int) or 0,
            TRANGTHAISPH=request.form.get("status", type=int) if request.form.get("status") is not None else 1,
            MADANHMUC=request.form.get("category_id", type=int),
        )
        if not product.TENSPH or product.DONGIA is None or product.DONGIA < 0:
            flash("Tên sản phẩm và giá hợp lệ là bắt buộc.", "danger")
        else:
            db.session.add(product)
            db.session.commit()
            flash("Đã thêm sản phẩm.", "success")
            return redirect(url_for("admin.products"))

    return render_template("admin_products.html", products=SanPham.query.order_by(SanPham.MASANPHAM.desc()).all())


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = SanPham.query.get_or_404(product_id)
    if request.method == "POST":
        product.TENSPH = request.form.get("name", "").strip()
        product.HINHANH = request.form.get("image", "").strip() or None
        product.DONGIA = request.form.get("price", type=float)
        product.MOTA = request.form.get("description", "").strip() or None
        product.SOLUONGTON = request.form.get("stock", type=int) or 0
        product.TRANGTHAISPH = request.form.get("status", type=int) if request.form.get("status") is not None else 1
        product.MADANHMUC = request.form.get("category_id", type=int)
        if not product.TENSPH or product.DONGIA is None or product.DONGIA < 0:
            flash("Tên sản phẩm và giá hợp lệ là bắt buộc.", "danger")
        else:
            db.session.commit()
            flash("Đã cập nhật sản phẩm.", "success")
            return redirect(url_for("admin.products"))

    return render_template("admin_product_form.html", product=product)


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


@admin_bp.route("/orders")
def orders():
    orders = DonHang.query.order_by(DonHang.MADONHANG.desc()).all()
    return render_template("admin_orders.html", orders=orders)


@admin_bp.post("/orders/<int:order_id>/status")
def update_order_status(order_id):
    order = DonHang.query.get_or_404(order_id)
    order.TRANGTHAI = request.form.get("status", type=int)
    order.NGAYDAT = order.NGAYDAT or date.today()
    db.session.commit()
    flash("Đã cập nhật trạng thái đơn hàng.", "success")
    return redirect(url_for("admin.orders"))