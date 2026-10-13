from flask import render_template, request

from app.services import product_service
from app.shop import shop_bp


@shop_bp.route("/products")
def products():
    keyword = request.args.get("q", default="", type=str).strip()
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort", default="", type=str)
    page = request.args.get("page", default=1, type=int)

    if sort not in product_service.SORT_OPTIONS:
        sort = ""

    min_price, max_price, warnings = product_service.normalize_price_range(
        request.args.get("min_price", ""),
        request.args.get("max_price", ""),
    )

    pagination = product_service.get_products(
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
    )

    return render_template(
        "products.html",
        products=pagination.items,
        categories=product_service.get_categories(),
        selected_category=category_id,
        selected_sort=sort or None,
        keyword=keyword or None,
        min_price=min_price,
        max_price=max_price,
        warnings=warnings,
        pagination=pagination,
    )


@shop_bp.route("/products/<int:id>")
def product_detail(id):
    # Giữ lại trang/bộ lọc để nút "Quay lại" về đúng chỗ cũ
    back_args = {
        "page": request.args.get("back_page", type=int),
        "category": request.args.get("back_category", type=int),
        "sort": request.args.get("back_sort") or None,
        "q": request.args.get("back_q") or None,
        "min_price": product_service.parse_price(request.args.get("back_min_price")),
        "max_price": product_service.parse_price(request.args.get("back_max_price")),
    }

    # Không có sản phẩm, hoặc sản phẩm đang bị ẩn -> báo "không tìm thấy"
    product = product_service.get_product_by_id(id)
    if product is None:
        return render_template(
            "product_detail.html",
            product=None,
            back_args=back_args,
        ), 404

    return render_template(
        "product_detail.html",
        product=product,
        back_args=back_args,
    )