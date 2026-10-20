from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.extensions import db
from app.models import SanPham
from app.services import product_service
from app.services.review_service import (
    ReviewError, add_review, get_rating_summary, get_reviews,
)
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

    avg_rating, review_count = get_rating_summary(product.MASANPHAM)
    return render_template(
        "product_detail.html",
        product=product,
        back_args=back_args,
        reviews=get_reviews(product.MASANPHAM),
        avg_rating=avg_rating,
        review_count=review_count,
    )


@shop_bp.route("/products/<int:id>/reviews", methods=["POST"])
def submit_review(id):
    product = db.session.get(SanPham, id)
    if product is None or product.TRANGTHAISPH != 1:
        abort(404)

    if not current_user.is_authenticated:
        flash("Vui lòng đăng nhập để gửi đánh giá.", "warning")
        return redirect(url_for("auth.login"))

    try:
        add_review(
            current_user.MANGUOIDUNG,
            id,
            request.form.get("rating"),
            request.form.get("comment"),
        )
        flash("Cảm ơn bạn đã đánh giá sản phẩm.", "success")
    except ReviewError as e:
        flash(str(e), "danger")

    return redirect(url_for("shop.product_detail", id=id))