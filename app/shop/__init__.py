from flask import Blueprint

shop_bp = Blueprint("shop", __name__)

from app.shop import product_routes
from app.shop import cart_routes