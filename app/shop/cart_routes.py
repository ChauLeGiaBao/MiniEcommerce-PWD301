import re
from datetime import date
from decimal import Decimal

from flask import render_template, request, redirect, url_for, session, flash, jsonify, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user, login_required

from app.shop import shop_bp
from app.extensions import db
from app.models import SanPham, DonHang, ChiTietDonHang
from app.shop.forms import CheckoutForm

PHONE_PATTERN = re.compile(r"^(\+84|0)\d{9,10}$")


class CheckoutError(Exception):
    """Lỗi nghiệp vụ khi checkout; transaction phải rollback."""


def _cart_count(cart_data=None):
    cart_data = session.get("cart", {}) if cart_data is None else cart_data
    count = 0
    for quantity in cart_data.values():
        try:
            quantity = int(quantity)
            if quantity > 0:
                count += quantity
        except (TypeError, ValueError):
            continue
    return count


def _json_requested():
    return request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.accept_mimetypes.best == "application/json"


def _cart_response(success, message, status=200, **extra):
    payload = {"success": success, "message": message, "cart_count": _cart_count()}
    payload.update(extra)
    return jsonify(payload), status


def _get_cart_items():
    """Đọc giỏ hàng từ session và loại bỏ dữ liệu hỏng/sản phẩm không tồn tại."""
    cart_data = session.get("cart", {})
    if not isinstance(cart_data, dict):
        cart_data = {}
        session["cart"] = cart_data
        session.modified = True

    cart_items = []
    total_price = Decimal("0")
    invalid_keys = []

    for key, raw_quantity in list(cart_data.items()):
        try:
            product_id = int(key)
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            invalid_keys.append(key)
            continue

        product = db.session.get(SanPham, product_id)
        if product is None or quantity <= 0:
            invalid_keys.append(key)
            continue

        subtotal = product.DONGIA * quantity
        total_price += subtotal
        cart_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})

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
        flash("Một số sản phẩm không còn tồn tại hoặc có số lượng không hợp lệ và đã được xóa khỏi giỏ hàng.", "warning")
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)


@shop_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = db.session.get(SanPham, product_id)
    if product is None or product.TRANGTHAISPH != 1:
        message = "Sản phẩm không tồn tại hoặc không còn được bán."
        if _json_requested():
            return _cart_response(False, message, 404)
        flash(message, "danger")
        return redirect(request.form.get("next") or url_for("shop.products"))

    try:
        cart_data = session.get("cart", {})
        if not isinstance(cart_data, dict):
            cart_data = {}
        current_qty = int(cart_data.get(str(product_id), 0))
    except (TypeError, ValueError):
        current_qty = 0
        cart_data = session.get("cart", {})
        if not isinstance(cart_data, dict):
            cart_data = {}

    if product.SOLUONGTON is None or product.SOLUONGTON <= 0:
        message = f"Sản phẩm {product.TENSPH} đã hết hàng."
        if _json_requested():
            return _cart_response(False, message, 409)
        flash(message, "danger")
        return redirect(request.form.get("next") or url_for("shop.products"))

    if current_qty + 1 > product.SOLUONGTON:
        message = f"Sản phẩm {product.TENSPH} chỉ còn {product.SOLUONGTON} sản phẩm."
        if _json_requested():
            return _cart_response(False, message, 409)
        flash(message, "danger")
        return redirect(request.form.get("next") or url_for("shop.products"))

    cart_data[str(product_id)] = current_qty + 1
    session["cart"] = cart_data
    session.modified = True
    message = f"Đã thêm {product.TENSPH} vào giỏ hàng."

    if _json_requested():
        return _cart_response(True, message, quantity=cart_data[str(product_id)])
    flash(message, "success")
    return redirect(request.form.get("next") or url_for("shop.cart"))


@shop_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart_data = session.get("cart", {})
    if not isinstance(cart_data, dict) or str(product_id) not in cart_data:
        message = "Sản phẩm không có trong giỏ hàng."
        if _json_requested():
            return _cart_response(False, message, 404)
        flash(message, "warning")
        return redirect(url_for("shop.cart"))

    source = request.get_json(silent=True) if request.is_json else request.form
    raw_quantity = source.get("quantity") if source else None
    try:
        # Do not silently coerce JSON floats (e.g. 1.8) or booleans to integers.
        if isinstance(raw_quantity, bool):
            raise ValueError("boolean is not a quantity")
        if isinstance(raw_quantity, float) and not raw_quantity.is_integer():
            raise ValueError("fractional quantity")
        quantity = int(raw_quantity)
        if isinstance(raw_quantity, str) and str(quantity) != raw_quantity.strip():
            raise ValueError("quantity must be an integer")
    except (TypeError, ValueError):
        quantity = 0

    if quantity <= 0:
        message = "Số lượng phải lớn hơn 0. Hãy dùng nút Xóa để bỏ sản phẩm khỏi giỏ hàng."
        if _json_requested():
            return _cart_response(False, message, 400)
        flash(message, "danger")
        return redirect(url_for("shop.cart"))

    product = db.session.get(SanPham, product_id)
    if product is None or product.TRANGTHAISPH != 1:
        message = "Sản phẩm không tồn tại hoặc không còn được bán."
        if _json_requested():
            return _cart_response(False, message, 404)
        cart_data.pop(str(product_id), None)
        session["cart"] = cart_data
        session.modified = True
        flash(message, "danger")
        return redirect(url_for("shop.cart"))

    if product.SOLUONGTON is None or product.SOLUONGTON <= 0 or quantity > product.SOLUONGTON:
        available = max(product.SOLUONGTON or 0, 0)
        message = f"Sản phẩm {product.TENSPH} chỉ còn {available} sản phẩm."
        if _json_requested():
            return _cart_response(False, message, 409, stock=available)
        flash(message, "danger")
        return redirect(url_for("shop.cart"))

    cart_data[str(product_id)] = quantity
    session["cart"] = cart_data
    session.modified = True
    subtotal = product.DONGIA * quantity
    if _json_requested():
        return _cart_response(True, "Đã cập nhật số lượng.", subtotal=float(subtotal), total_quantity=quantity)
    flash("Đã cập nhật số lượng.", "success")
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})
    if not isinstance(cart_data, dict):
        cart_data = {}
    existed = str(product_id) in cart_data
    cart_data.pop(str(product_id), None)
    session["cart"] = cart_data
    session.modified = True
    message = "Đã xóa sản phẩm khỏi giỏ hàng." if existed else "Sản phẩm không có trong giỏ hàng."
    if _json_requested():
        return _cart_response(True, message)
    flash(message, "success" if existed else "warning")
    return redirect(url_for("shop.cart"))


def _render_checkout(cart_items, total_price, form=None):
    return render_template("checkout.html", cart_items=cart_items, total_price=total_price,
                           form=form or CheckoutForm())


@shop_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items, total_price, invalid_keys = _get_cart_items()
    if invalid_keys:
        flash("Một số sản phẩm không còn tồn tại hoặc có số lượng không hợp lệ. Vui lòng kiểm tra lại.", "warning")
        return redirect(url_for("shop.cart"))
    if not cart_items:
        flash("Giỏ hàng đang trống.", "warning")
        return redirect(url_for("shop.products"))

    form = CheckoutForm()
    if request.method == "GET":
        return _render_checkout(cart_items, total_price, form)

    if not form.validate_on_submit():
        return _render_checkout(cart_items, total_price, form), 400

    fullname = form.fullname.data.strip()
    address = form.address.data.strip()
    phone = re.sub(r"\s+", "", form.phone.data or "")

    try:
        # Re-read each product and validate stock immediately before creating the order.
        order_total = Decimal("0")
        lines = []
        for item in cart_items:
            product = db.session.execute(
                db.select(SanPham)
                .where(SanPham.MASANPHAM == item["product"].MASANPHAM)
                .with_for_update()
            ).scalar_one_or_none()
            quantity = item["quantity"]
            if product is None or product.TRANGTHAISPH != 1:
                raise CheckoutError("Có sản phẩm không còn được bán. Vui lòng kiểm tra lại giỏ hàng.")
            if quantity <= 0:
                raise CheckoutError("Số lượng sản phẩm không hợp lệ.")
            if product.SOLUONGTON is None or quantity > product.SOLUONGTON:
                raise CheckoutError(f"Sản phẩm {product.TENSPH} chỉ còn {max(product.SOLUONGTON or 0, 0)} sản phẩm.")
            order_total += product.DONGIA * quantity
            lines.append((product, quantity))

        user_id = current_user.MANGUOIDUNG if current_user.is_authenticated else None
        order = DonHang(
            MANGUOIDUNG=user_id, NGAYDAT=date.today(), TONGGIATRI=order_total, TRANGTHAI=0,
            HOTENNHAN=fullname, DIACHIGIAO=address, SDTNHAN=phone,
        )
        db.session.add(order)
        db.session.flush()
        for product, quantity in lines:
            db.session.add(ChiTietDonHang(
                MADONHANG=order.MADONHANG, MASANPHAM=product.MASANPHAM, SOLUONG=quantity,
            ))
            product.SOLUONGTON -= quantity

        db.session.commit()
        order_id = order.MADONHANG
    except CheckoutError as error:
        db.session.rollback()
        flash(str(error), "danger")
        return redirect(url_for("shop.cart"))
    except SQLAlchemyError:
        db.session.rollback()
        flash("Không thể tạo đơn hàng. Vui lòng thử lại.", "danger")
        return _render_checkout(cart_items, total_price, form), 500

    # Cart is cleared only after the database transaction commits successfully.
    session.pop("cart", None)
    session["last_order_id"] = order_id
    return redirect(url_for("shop.order_success", order_id=order_id))


@shop_bp.route("/my-orders")
@login_required
def my_orders():
    orders = (DonHang.query
              .filter_by(MANGUOIDUNG=current_user.MANGUOIDUNG)
              .order_by(DonHang.NGAYDAT.desc(), DonHang.MADONHANG.desc())
              .all())
    return render_template("my_orders.html", orders=orders)


@shop_bp.route("/my-orders/<int:order_id>")
@login_required
def my_order_detail(order_id):
    order = DonHang.query.filter_by(
        MADONHANG=order_id, MANGUOIDUNG=current_user.MANGUOIDUNG
    ).first_or_404()
    return render_template("my_order_detail.html", order=order)


@shop_bp.route("/order-success/<int:order_id>", methods=["GET"])
def order_success(order_id):
    order = db.session.get(DonHang, order_id)
    if order is None:
        flash("Không tìm thấy đơn hàng.", "warning")
        return redirect(url_for("shop.products"))

    is_last_order = (
        not current_user.is_authenticated
        and order.MANGUOIDUNG is None
        and session.get("last_order_id") == order_id
    )
    is_owner = current_user.is_authenticated and order.MANGUOIDUNG == current_user.MANGUOIDUNG
    is_admin = current_user.is_authenticated and (getattr(current_user, "ROLE", "") or "").lower() == "admin"
    if not (is_last_order or is_owner or is_admin):
        abort(403)

    return render_template("order_success.html", order=order)
