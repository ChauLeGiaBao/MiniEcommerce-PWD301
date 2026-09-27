from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from app.shop import shop_bp
from app.models import SanPham


def _get_cart_items():
    cart_data = session.get("cart", {})

    cart_items = []
    total_price = 0

    for product_id, quantity in cart_data.items():

        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        product = SanPham.query.get(product_id)

        if product and quantity > 0:
            subtotal = product.DONGIA * quantity

            total_price += subtotal

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    return cart_items, total_price


@shop_bp.route("/cart")
def cart():
    cart_items, total_price = _get_cart_items()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price
    )


@shop_bp.route(
    "/cart/add/<int:product_id>",
    methods=["POST"]
)
def add_to_cart(product_id):
    product = SanPham.query.get_or_404(product_id)

    cart_data = session.get("cart", {})

    key = str(product_id)

    cart_data[key] = int(
        cart_data.get(key, 0)
    ) + 1

    session["cart"] = cart_data
    session.modified = True

    flash(
        f"Đã thêm {product.TENSPH} vào giỏ hàng.",
        "success"
    )

    return redirect(
        url_for("shop.cart")
    )


@shop_bp.route(
    "/cart/update/<int:product_id>",
    methods=["POST"]
)
def update_cart(product_id):
    cart_data = session.get("cart", {})

    try:
        quantity = int(
            request.form.get("quantity", 1)
        )
    except (TypeError, ValueError):
        quantity = 1

    key = str(product_id)

    if key in cart_data:

        if quantity > 0:
            cart_data[key] = quantity
        else:
            cart_data.pop(key, None)

        session["cart"] = cart_data
        session.modified = True

    return redirect(
        url_for("shop.cart")
    )


@shop_bp.route(
    "/cart/remove/<int:product_id>",
    methods=["POST"]
)
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})

    cart_data.pop(
        str(product_id),
        None
    )

    session["cart"] = cart_data
    session.modified = True

    return redirect(
        url_for("shop.cart")
    )


@shop_bp.route(
    "/checkout",
    methods=["GET", "POST"]
)
def checkout():
    cart_items, total_price = _get_cart_items()

    if not cart_items:
        flash(
            "Giỏ hàng đang trống.",
            "warning"
        )

        return redirect(
            url_for("shop.products")
        )

    if request.method == "POST":

        fullname = request.form.get(
            "fullname",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        if not fullname or not address or not phone:
            flash(
                "Vui lòng nhập đầy đủ thông tin.",
                "danger"
            )

            return render_template(
                "checkout.html",
                cart_items=cart_items,
                total_price=total_price
            )

        # Tuần 2 Tuấn bổ sung ở đây:
        # - tạo DONHANG
        # - tạo CHITIETDONHANG
        # - update tồn kho
        # - db.session.commit()

        session.pop("cart", None)

        return render_template(
            "order_success.html"
        )

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_price=total_price
    )