from flask import render_template, request

from app.extensions import db
from app.shop import shop_bp
from app.models import SanPham, DanhMuc


PER_PAGE = 8

SORT_OPTIONS = {
    "price_asc": SanPham.DONGIA.asc(),
    "price_desc": SanPham.DONGIA.desc(),
    "name_asc": SanPham.TENSPH.asc(),
}


@shop_bp.route("/products")
def products():
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort", default="", type=str)
    keyword = request.args.get("q", default="", type=str).strip()
    page = request.args.get("page", default=1, type=int)

    if sort not in SORT_OPTIONS:
        sort = ""

    if page < 1:
        page = 1

    # Chỉ hiện sản phẩm đang bán (TRANGTHAISPH = 1), sản phẩm "Tạm ẩn" không hiện ngoài shop
    query = SanPham.query.filter(SanPham.TRANGTHAISPH == 1)

    if category_id:
        query = query.filter(SanPham.MADANHMUC == category_id)

    if keyword:
        query = query.filter(SanPham.TENSPH.ilike(f"%{keyword}%"))

    # Luôn sắp thêm theo mã SP để phân trang ổn định (SQL Server bắt buộc có ORDER BY)
    if sort:
        query = query.order_by(SORT_OPTIONS[sort], SanPham.MASANPHAM.asc())
    else:
        query = query.order_by(SanPham.MASANPHAM.asc())

    pagination = query.paginate(
        page=page,
        per_page=PER_PAGE,
        error_out=False
    )

    categories = DanhMuc.query.order_by(DanhMuc.MADANHMUC.asc()).all()

    return render_template(
        "products.html",
        products=pagination.items,
        categories=categories,
        selected_category=category_id,
        selected_sort=sort or None,
        keyword=keyword or None,
        pagination=pagination
    )


@shop_bp.route("/products/<int:id>")
def product_detail(id):
    # Giữ lại trang/bộ lọc để nút "Quay lại" về đúng chỗ cũ
    back_args = {
        "page": request.args.get("back_page", type=int),
        "category": request.args.get("back_category", type=int),
        "sort": request.args.get("back_sort") or None,
        "q": request.args.get("back_q") or None,
    }

    product = db.session.get(SanPham, id)

    # Không có sản phẩm, hoặc sản phẩm đang bị ẩn -> báo "không tìm thấy"
    if product is None or product.TRANGTHAISPH != 1:
        return render_template(
            "product_detail.html",
            product=None,
            back_args=back_args
        ), 404

    return render_template(
        "product_detail.html",
        product=product,
        back_args=back_args
    )