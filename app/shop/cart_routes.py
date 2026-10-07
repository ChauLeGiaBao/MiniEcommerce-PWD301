import re
from datetime import date

from flask import render_template, request, redirect, url_for, session, flash
from sqlalchemy.exc import SQLAlchemyError

from app.shop import shop_bp
from app.extensions import db
from app.models import SanPham, DonHang, ChiTietDonHang

PHONE_PATTERN = re.compile(r"^(\+84|0)\d{9,10}$")


class CheckoutError(Exception):
    """Lỗi nghiệp vụ khi checkout (vd: vượt tồn kho). Dùng để rollback."""


def _get_cart_items():
    """Đọc giỏ hàng từ session, tự dọn các mục không hợp lệ.

    Trả về (cart_items, total_price, removed_names).
    Các mục lỗi (sản phẩm không tồn tại, số lượng sai) bị xóa khỏi session
    để người dùng không bị kẹt không checkout được.
    """
    cart_data = session.get("cart", {})
    cart_items = []
    total_price = 0
    invalid_keys = []

    for key, quantity in cart_data.items():
        try:
            product_id = int(key)
            quantity = int(quantity)
        except (TypeError, ValueError):
            invalid_keys.append(key)
            continue

        product = db.session.get(SanPham, product_id)

        if product is None or quantity <= 0:
            invalid_keys.append(key)
            continue

        subtotal = product.DONGIA * quantity
        total_price += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    if invalid_keys:
        for key in invalid_keys:
            cart_data.pop(key, None)
        session["cart"] = cart_data
        session.modified = True

    return cart_items, total_price, invalid_keys


@shop_bp.route("/cart")
def cart():
    cart_items, total_price, invalid_keys = _get_cart_items()

    if invalid_keys:
        flash("Một số sản phẩm không còn tồn tại và đã được xóa khỏi giỏ hàng.", "warning")

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price,
    )


@shop_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = db.get_or_404(SanPham, product_id)
    cart_data = session.get("cart", {})
    key = str(product_id)

    current_qty = int(cart_data.get(key, 0))

    if current_qty + 1 > product.SOLUONGTON:
        flash(f"Sản phẩm {product.TENSPH} chỉ còn {product.SOLUONGTON} sản phẩm.", "danger")
        return redirect(url_for("shop.cart"))

    cart_data[key] = current_qty + 1
    session["cart"] = cart_data
    session.modified = True

    flash(f"Đã thêm {product.TENSPH} vào giỏ hàng.", "success")
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart_data = session.get("cart", {})
    key = str(product_id)

    if key not in cart_data:
        return redirect(url_for("shop.cart"))

    try:
        quantity = int(request.form.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart_data.pop(key, None)
    else:
        product = db.session.get(SanPham, product_id)
        if product is None:
            cart_data.pop(key, None)
        elif quantity > product.SOLUONGTON:
            cart_data[key] = max(product.SOLUONGTON, 1)
            flash(f"Sản phẩm {product.TENSPH} chỉ còn {product.SOLUONGTON} sản phẩm.", "danger")
        else:
            cart_data[key] = quantity

    session["cart"] = cart_data
    session.modified = True
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})
    cart_data.pop(str(product_id), None)

    session["cart"] = cart_data
    session.modified = True

    return redirect(url_for("shop.cart"))


def _render_checkout(cart_items, total_price):
    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_price=total_price,
    )


@shop_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items, total_price, invalid_keys = _get_cart_items()

    if invalid_keys:
        flash("Một số sản phẩm không còn tồn tại và đã được xóa khỏi giỏ hàng. Vui lòng kiểm tra lại.", "warning")
        return redirect(url_for("shop.cart"))

    if not cart_items:
        flash("Giỏ hàng đang trống.", "warning")
        return redirect(url_for("shop.products"))

    if request.method == "GET":
        return _render_checkout(cart_items, total_price)

    # ----- POST: validate -----
    fullname = request.form.get("fullname", "").strip()
    address = request.form.get("address", "").strip()
    phone = request.form.get("phone", "").strip().replace(" ", "")

    if not fullname or not address or not phone:
        flash("Vui lòng nhập đầy đủ họ tên, địa chỉ và số điện thoại.", "danger")
        return _render_checkout(cart_items, total_price)

    if not PHONE_PATTERN.match(phone):
        flash("Số điện thoại không hợp lệ.", "danger")
        return _render_checkout(cart_items, total_price)

    # ----- POST: tạo đơn trong 1 transaction -----
    try:
        order_total = 0
        lines = []

        # Đọc lại sản phẩm (khóa dòng nếu DB hỗ trợ) để kiểm tra tồn kho và giá mới nhất
        for item in cart_items:
            product = db.session.execute(
                db.select(SanPham)
                .where(SanPham.MASANPHAM == item["product"].MASANPHAM)
                .with_for_update()
            ).scalar_one_or_none()
            quantity = item["quantity"]

            if product is None:
                raise CheckoutError("Có sản phẩm không còn tồn tại. Vui lòng kiểm tra lại giỏ hàng.")

            if quantity > product.SOLUONGTON:
                raise CheckoutError(
                    f"Sản phẩm {product.TENSPH} chỉ còn {product.SOLUONGTON} sản phẩm."
                )

            order_total += product.DONGIA * quantity
            lines.append((product, quantity))

        order = DonHang(
            MANGUOIDUNG=None,
            NGAYDAT=date.today(),
            TONGGIATRI=order_total,
            TRANGTHAI=0,
            HOTENNHAN=fullname,
            DIACHIGIAO=address,
            SDTNHAN=phone,
        )
        db.session.add(order)
        db.session.flush()  # lấy MADONHANG

        for product, quantity in lines:
            db.session.add(ChiTietDonHang(
                MADONHANG=order.MADONHANG,
                MASANPHAM=product.MASANPHAM,
                SOLUONG=quantity,
            ))
            product.SOLUONGTON -= quantity

        db.session.commit()

    except CheckoutError as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("shop.cart"))

    except SQLAlchemyError:
        db.session.rollback()
        flash("Không thể tạo đơn hàng. Vui lòng thử lại.", "danger")
        return _render_checkout(cart_items, total_price)

    # Chỉ clear cart SAU KHI commit thành công
    session.pop("cart", None)

    return render_template("order_success.html", order=order)
