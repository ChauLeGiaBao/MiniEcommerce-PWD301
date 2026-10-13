"""Service chung cho Product: toàn bộ logic query sản phẩm nằm ở đây.

Route (shop) và API (Bảo/Long) chỉ cần gọi các hàm bên dưới, không tự viết lại query.

Quy ước:
- TRANGTHAISPH: 1 = Đang bán (Active), 0 = Tạm ẩn (Inactive).
  Trang shop chỉ hiển thị sản phẩm Active.
- Sort "newest": chưa có cột ngày tạo nên dùng MASANPHAM DESC (ID lớn = mới hơn).
"""
import re
from decimal import Decimal

from sqlalchemy import or_

from app.extensions import db
from app.models import DanhMuc, SanPham

STATUS_ACTIVE = 1
STATUS_INACTIVE = 0

PER_PAGE = 8

# Giá chỉ nhận số không âm: tối đa 15 chữ số nguyên + tối đa 2 chữ số thập phân
_PRICE_PATTERN = re.compile(r"\d{1,15}(\.\d{1,2})?")

SORT_OPTIONS = {
    "newest": SanPham.MASANPHAM.desc(),
    "price_asc": SanPham.DONGIA.asc(),
    "price_desc": SanPham.DONGIA.desc(),
    "name_asc": SanPham.TENSPH.asc(),
    "name_desc": SanPham.TENSPH.desc(),
}


def parse_price(raw):
    """Chuỗi -> Decimal. Rỗng, âm, chữ, quá lớn -> None."""
    if raw is None:
        return None
    raw = str(raw).strip().replace(" ", "")
    if not _PRICE_PATTERN.fullmatch(raw):
        return None
    return Decimal(raw)


def normalize_price_range(min_raw, max_raw):
    """Kiểm tra khoảng giá người dùng nhập.

    Trả về (min_price, max_price, warnings). Không bao giờ raise lỗi:
    - giá không hợp lệ (chữ, âm...) -> bỏ qua và thêm cảnh báo
    - min > max -> tự đổi chỗ và thêm cảnh báo
    """
    warnings = []
    min_price = parse_price(min_raw)
    max_price = parse_price(max_raw)

    if min_raw and min_raw.strip() and min_price is None:
        warnings.append("Giá tối thiểu không hợp lệ nên đã được bỏ qua.")
    if max_raw and max_raw.strip() and max_price is None:
        warnings.append("Giá tối đa không hợp lệ nên đã được bỏ qua.")

    if min_price is not None and max_price is not None and min_price > max_price:
        min_price, max_price = max_price, min_price
        warnings.append("Giá tối thiểu lớn hơn giá tối đa nên hai giá trị đã được đổi chỗ.")

    return min_price, max_price, warnings


def _like_escape(text):
    """Escape ký tự đặc biệt của LIKE (kể cả '[' của SQL Server) để tìm đúng nghĩa đen."""
    for ch in ("\\", "%", "_", "["):
        text = text.replace(ch, "\\" + ch)
    return text


def get_products(keyword="", category_id=None, min_price=None, max_price=None,
                 sort="", page=1, per_page=PER_PAGE):
    """Danh sách sản phẩm đang bán, có tìm kiếm, lọc, sắp xếp, phân trang."""
    query = SanPham.query.filter(SanPham.TRANGTHAISPH == STATUS_ACTIVE)

    keyword = (keyword or "").strip()
    if keyword:
        pattern = f"%{_like_escape(keyword)}%"
        query = query.filter(or_(
            SanPham.TENSPH.ilike(pattern, escape="\\"),
            SanPham.MOTA.ilike(pattern, escape="\\"),
        ))

    if category_id:
        query = query.filter(SanPham.MADANHMUC == category_id)

    if min_price is not None:
        query = query.filter(SanPham.DONGIA >= min_price)
    if max_price is not None:
        query = query.filter(SanPham.DONGIA <= max_price)

    # Luôn có ORDER BY (SQL Server bắt buộc khi phân trang).
    # SQL Server không cho 1 cột xuất hiện 2 lần trong ORDER BY, nên "newest"
    # (đã sắp theo MASANPHAM) không được thêm mã SP lần nữa.
    if sort == "newest":
        query = query.order_by(SanPham.MASANPHAM.desc())
    elif sort in SORT_OPTIONS:
        query = query.order_by(SORT_OPTIONS[sort], SanPham.MASANPHAM.asc())
    else:
        query = query.order_by(SanPham.MASANPHAM.asc())

    return query.paginate(page=max(page or 1, 1), per_page=per_page, error_out=False)


def get_product_by_id(product_id, active_only=True):
    """Lấy 1 sản phẩm. Mặc định chỉ trả sản phẩm đang bán (Inactive -> None)."""
    product = db.session.get(SanPham, product_id)
    if product is None:
        return None
    if active_only and product.TRANGTHAISPH != STATUS_ACTIVE:
        return None
    return product


def get_categories():
    return DanhMuc.query.order_by(DanhMuc.MADANHMUC.asc()).all()


def is_available(product, quantity=1):
    """Sản phẩm có bán được với số lượng `quantity` không?

    Dùng cho Cart/Checkout: sản phẩm phải tồn tại, đang bán (Active) và đủ tồn kho.
    """
    if product is None:
        return False
    if product.TRANGTHAISPH != STATUS_ACTIVE:
        return False
    return (product.SOLUONGTON or 0) >= quantity