from flask import jsonify
from app.api import api_bp
from app.models import SanPham


def product_to_dict(product):
    return {
        "id": product.MASANPHAM,
        "name": product.TENSPH,
        "image": product.HINHANH,
        "price": float(product.DONGIA) if product.DONGIA is not None else None,
        "description": product.MOTA,
        "stock": product.SOLUONGTON if product.SOLUONGTON is not None else 0,
        "status": product.TRANGTHAISPH if product.TRANGTHAISPH is not None else 1,
        "category_id": product.MADANHMUC,
    }


@api_bp.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "API is running"
    })


@api_bp.route("/products")
def products():
    products = SanPham.query.order_by(SanPham.MASANPHAM.asc()).all()
    return jsonify({
        "data": [product_to_dict(product) for product in products],
        "count": len(products),
    })


@api_bp.route("/products/<int:product_id>")
def product_detail(product_id):
    product = SanPham.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product_to_dict(product))