
from flask import jsonify, request

from app.api import api_bp
from app.services import product_service


def product_to_dict(product):
    return {
        "id": product.MASANPHAM,
        "name": product.TENSPH,
        "image": product.HINHANH,
        "price": float(product.DONGIA)
        if product.DONGIA is not None else None,
        "description": product.MOTA,
        "stock": product.SOLUONGTON or 0,
        "status": product.TRANGTHAISPH,
        "category_id": product.MADANHMUC,
    }


def positive_int_param(name, default, maximum=None):
    raw = request.args.get(name)

    if raw is None or raw == "":
        return default

    try:
        value = int(raw)
    except ValueError:
        return None

    if value < 1:
        return None

    if maximum is not None and value > maximum:
        return None

    return value


@api_bp.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "API is running"
    })


@api_bp.get("/products")
def products():
    keyword = request.args.get("q", "").strip()
    sort = request.args.get("sort", "").strip()

    page = positive_int_param("page", 1)
    per_page = positive_int_param("per_page", 8, 50)

    if page is None or per_page is None:
        return jsonify({
            "error": "Invalid pagination parameters"
        }), 400

    category_raw = request.args.get("category", "").strip()
    category_id = None

    if category_raw:
        try:
            category_id = int(category_raw)
            if category_id < 1:
                raise ValueError()
        except ValueError:
            return jsonify({
                "error": "Invalid category"
            }), 400

    if sort and sort not in product_service.SORT_OPTIONS:
        return jsonify({
            "error": "Invalid sort option"
        }), 400

    min_price, max_price, warnings = (
        product_service.normalize_price_range(
            request.args.get("min_price", ""),
            request.args.get("max_price", "")
        )
    )

    pagination = product_service.get_products(
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "data": [
            product_to_dict(product)
            for product in pagination.items
        ],
        "count": pagination.total,
        "returned_count": len(pagination.items),
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "warnings": warnings,
    }), 200


@api_bp.get("/products/<int:product_id>")
def product_detail(product_id):
    product = product_service.get_product_by_id(
        product_id,
        active_only=True
    )

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify(product_to_dict(product)), 200
