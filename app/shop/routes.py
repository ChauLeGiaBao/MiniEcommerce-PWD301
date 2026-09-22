from flask import render_template, request
from app.shop import shop_bp
from app.models import SanPham, DanhMuc


@shop_bp.route("/products")
def products():
    category_id = request.args.get('category', type=int)
    sort = request.args.get('sort', default='', type=str)
    page = request.args.get('page', default=1, type=int)
    per_page = 8

    query = SanPham.query
    if category_id:
        query = query.filter_by(MADANHMUC=category_id)

    if sort == 'price_asc':
        query = query.order_by(SanPham.DONGIA.asc())
    elif sort == 'price_desc':
        query = query.order_by(SanPham.DONGIA.desc())
    elif sort == 'name_asc':
        query = query.order_by(SanPham.TENSPH.asc())
    else:
        query = query.order_by(SanPham.MASANPHAM.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    categories = DanhMuc.query.all()

    return render_template(
        "products.html",
        products=products,
        categories=categories,
        selected_category=category_id,
        selected_sort=sort,
        pagination=pagination
    )


@shop_bp.route("/products/<int:id>")
def product_detail(id):
    product = SanPham.query.get_or_404(id)
    back_page = request.args.get('back_page', default=1, type=int)
    back_category = request.args.get('back_category', default='', type=str)
    back_sort = request.args.get('back_sort', default='', type=str)
    return render_template(
        "product_detail.html",
        product=product,
        back_page=back_page,
        back_category=back_category,
        back_sort=back_sort
    )


@shop_bp.route("/cart")
def cart():
    return render_template("cart.html")


@shop_bp.route("/checkout")
def checkout():
    return render_template("checkout.html")
