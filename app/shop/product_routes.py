from flask import render_template, request
from app.shop import shop_bp
from app.models import SanPham, DanhMuc


@shop_bp.route("/products")
def products():
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort", default="", type=str)
    page = request.args.get("page", default=1, type=int)

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
        per_page=8,
        error_out=False
    )

    categories = DanhMuc.query.all()

    return render_template(
        "products.html",
        products=pagination.items,
        categories=categories,
        selected_category=category_id,
        selected_sort=sort,
        pagination=pagination
    )


@shop_bp.route("/products/<int:id>")
def product_detail(id):
    product = SanPham.query.get_or_404(id)

    return render_template(
        "product_detail.html",
        product=product
    )