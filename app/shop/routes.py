from flask import render_template
from app.shop import shop_bp


@shop_bp.route("/products")
def products():
    return render_template("products.html")


@shop_bp.route("/cart")
def cart():
    return render_template("cart.html")


@shop_bp.route("/checkout")
def checkout():
    return render_template("checkout.html")