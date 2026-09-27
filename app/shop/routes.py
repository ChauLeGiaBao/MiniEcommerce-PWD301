from flask import render_template, request, redirect, url_for, session, flash
from app.shop import shop_bp
from app.models import SanPham, DanhMuc


def _get_cart_items():
    """Đọc giỏ hàng từ session và trả về danh sách item + tổng tiền."""
    cart_data = session.get("cart", {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart_data.items():
        try:
            product_id_int = int(product_id)
            quantity_int = int(quantity)
        except (TypeError, ValueError):
            continue

        if quantity_int <= 0:
            continue

        product = SanPham.query.get(product_id_int)
        if product:
            subtotal = product.DONGIA * quantity_int
            total_price += subtotal
            cart_items.append(
                {
                    "product": product,
                    "quantity": quantity_int,
                    "subtotal": subtotal,
                }
            )

    return cart_items, total_price


@shop_bp.route("/products")
def products():
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort", default="", type=str)
    page = request.args.get("page", default=1, type=int)
    per_page = 8

    query = SanPham.query

    if category_id:
        query = query.filter_by(MADANHMUC=category_id)

    if sort == "price_asc":
        query = query.order_by(SanPham.DONGIA.asc())
    elif sort == "price_desc":
        query = query.order_by(SanPham.DONGIA.desc())
    elif sort == "name_asc":
        query = query.order_by(SanPham.TENSPH.asc())
    else:
        query = query.order_by(SanPham.MASANPHAM.asc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    products = pagination.items
    categories = DanhMuc.query.all()

    return render_template(
        "products.html",
        products=products,
        categories=categories,
        selected_category=category_id,
        selected_sort=sort,
        pagination=pagination,
    )


@shop_bp.route("/products/<int:id>")
def product_detail(id):
    product = SanPham.query.get_or_404(id)

    back_page = request.args.get("back_page", default=1, type=int)
    back_category = request.args.get("back_category", default="", type=str)
    back_sort = request.args.get("back_sort", default="", type=str)

    return render_template(
        "product_detail.html",
        product=product,
        back_page=back_page,
        back_category=back_category,
        back_sort=back_sort,
    )


@shop_bp.route("/cart")
def cart():
    cart_items, total_price = _get_cart_items()
    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price,
    )


@shop_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = SanPham.query.get_or_404(product_id)

    cart_data = session.get("cart", {})
    key = str(product.MASANPHAM)
    cart_data[key] = int(cart_data.get(key, 0)) + 1

    session["cart"] = cart_data
    session.modified = True

    flash(f"Đã thêm {product.TENSPH} vào giỏ hàng.", "success")

    next_url = request.form.get("next")
    if next_url:
        return redirect(next_url)

    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart_data = session.get("cart", {})

    try:
        quantity = int(request.form.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    key = str(product_id)

    if key in cart_data:
        if quantity > 0:
            cart_data[key] = quantity
            flash("Đã cập nhật số lượng sản phẩm.", "success")
        else:
            cart_data.pop(key, None)
            flash("Đã xóa sản phẩm khỏi giỏ hàng.", "info")

        session["cart"] = cart_data
        session.modified = True

    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})
    key = str(product_id)

    if key in cart_data:
        cart_data.pop(key, None)
        session["cart"] = cart_data
        session.modified = True
        flash("Đã xóa sản phẩm khỏi giỏ hàng.", "info")

    return redirect(url_for("shop.cart"))


@shop_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items, total_price = _get_cart_items()

    if not cart_items:
        flash("Giỏ hàng đang trống.", "warning")
        return redirect(url_for("shop.products"))

    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()

        if not fullname or not address or not phone:
            flash("Vui lòng nhập đầy đủ thông tin nhận hàng.", "danger")
            return render_template(
                "checkout.html",
                cart_items=cart_items,
                total_price=total_price,
            )

        # Hiện tại phần của Tuấn mới xử lý giỏ hàng bằng session.
        # Khi nhóm nối chức năng tạo DONHANG/CHITIETDONHANG vào DB,
        # đoạn này sẽ là vị trí lưu đơn hàng.
        session.pop("cart", None)
        flash("Đặt hàng thành công! Cảm ơn bạn đã mua sắm.", "success")
        return redirect(url_for("shop.products"))

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_price=total_price,
    )
