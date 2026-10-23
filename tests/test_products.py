import html
import re
from urllib.parse import parse_qs, urlparse

from app.extensions import db
from app.models import SanPham
from app.services import product_service

NO_RESULT = "Không có sản phẩm phù hợp"


def card_names(page_html):
    """Tên sản phẩm trên trang danh sách, theo đúng thứ tự hiển thị."""
    found = re.findall(r'<h5 class="card-title">\s*<a [^>]*>\s*(.+?)\s*</a>', page_html, re.S)
    return [html.unescape(name) for name in found]


def get_names(client, url):
    response = client.get(url)
    assert response.status_code == 200
    return card_names(response.get_data(as_text=True))


# ---------------------------------------------------------------- trang danh sách
def test_products_page_ok_and_hides_inactive(client):
    response = client.get("/products")
    assert response.status_code == 200

    names = card_names(response.get_data(as_text=True))
    assert names == ["Alpha Phone", "Beta Phone", "Gamma Laptop", "Delta Phone"]
    assert "Hidden Phone" not in names  # Inactive không hiện ở shop


# ---------------------------------------------------------------- search
def test_search_by_name(client):
    assert get_names(client, "/products?q=alpha") == ["Alpha Phone"]


def test_search_is_case_insensitive(client):
    assert get_names(client, "/products?q=ALPHA") == ["Alpha Phone"]


def test_search_in_description(client):
    assert get_names(client, "/products?q=amoled") == ["Beta Phone"]
    assert get_names(client, "/products?q=chip") == ["Alpha Phone", "Gamma Laptop"]


def test_search_no_result_shows_message(client):
    response = client.get("/products?q=khongcosanphamnay")
    assert response.status_code == 200
    assert NO_RESULT in response.get_data(as_text=True)


def test_search_empty_keyword_returns_all(client):
    assert len(get_names(client, "/products?q=")) == 4
    assert len(get_names(client, "/products?q=%20%20")) == 4


def test_search_special_characters_do_not_crash(client):
    for keyword in ["%25", "_", "[", "%5B", "'", "%22", "%5C", "%3Cscript%3E"]:
        response = client.get(f"/products?q={keyword}")
        assert response.status_code == 200, keyword
        # Ký tự đặc biệt được tìm theo nghĩa đen nên không khớp sản phẩm nào
        assert NO_RESULT in response.get_data(as_text=True), keyword


# ---------------------------------------------------------------- category
def test_category_filter(client):
    assert get_names(client, "/products?category=11") == ["Alpha Phone", "Beta Phone", "Delta Phone"]
    assert get_names(client, "/products?category=12") == ["Gamma Laptop"]


def test_empty_or_unknown_category_shows_message(client):
    for category in (13, 999):
        response = client.get(f"/products?category={category}")
        assert response.status_code == 200
        assert NO_RESULT in response.get_data(as_text=True)


def test_category_all_button_keeps_other_filters(client):
    page = client.get("/products?category=11&q=alpha&min_price=100&sort=newest").get_data(as_text=True)
    all_link = next(h for h in re.findall(r'href="(/products\?[^"]*)"', page) if "category" not in h)
    query = parse_qs(urlparse(html.unescape(all_link)).query)

    assert "category" not in query
    assert query["q"] == ["alpha"]
    assert query["min_price"] == ["100"]
    assert query["sort"] == ["newest"]


# ---------------------------------------------------------------- price
def test_min_price(client):
    assert get_names(client, "/products?min_price=20000000") == ["Alpha Phone", "Gamma Laptop"]


def test_max_price(client):
    assert get_names(client, "/products?max_price=10000000") == ["Delta Phone"]


def test_price_range_is_inclusive(client):
    assert get_names(client, "/products?min_price=18000000&max_price=22000000") == ["Alpha Phone", "Beta Phone"]


def test_min_greater_than_max_is_swapped_with_warning(client):
    response = client.get("/products?min_price=30000000&max_price=1000000")
    assert response.status_code == 200

    page = response.get_data(as_text=True)
    assert len(card_names(page)) == 4
    assert "đổi chỗ" in page


def test_invalid_price_is_ignored_with_warning(client):
    for value in ["abc", "-5", "1e5", "12.345", "9" * 30]:
        response = client.get(f"/products?min_price={value}")
        assert response.status_code == 200, value

        page = response.get_data(as_text=True)
        assert len(card_names(page)) == 4, value
        assert "không hợp lệ" in page, value


def test_empty_price_has_no_warning(client):
    page = client.get("/products?min_price=&max_price=").get_data(as_text=True)
    assert len(card_names(page)) == 4
    assert "không hợp lệ" not in page


# ---------------------------------------------------------------- sort
def test_sorts(client):
    assert get_names(client, "/products?sort=price_asc") == ["Delta Phone", "Beta Phone", "Alpha Phone", "Gamma Laptop"]
    assert get_names(client, "/products?sort=price_desc") == ["Gamma Laptop", "Alpha Phone", "Beta Phone", "Delta Phone"]
    assert get_names(client, "/products?sort=name_asc") == ["Alpha Phone", "Beta Phone", "Delta Phone", "Gamma Laptop"]
    assert get_names(client, "/products?sort=name_desc") == ["Gamma Laptop", "Delta Phone", "Beta Phone", "Alpha Phone"]


def test_sort_newest_puts_larger_id_first(client):
    # Quy ước: chưa có cột ngày tạo nên "mới nhất" = MASANPHAM lớn nhất
    assert get_names(client, "/products?sort=newest") == ["Delta Phone", "Gamma Laptop", "Beta Phone", "Alpha Phone"]


def test_unknown_sort_is_ignored(client):
    assert get_names(client, "/products?sort=khong-co") == ["Alpha Phone", "Beta Phone", "Gamma Laptop", "Delta Phone"]


def test_search_category_price_sort_together(client):
    url = "/products?q=phone&category=11&min_price=5000000&max_price=25000000&sort=newest"
    assert get_names(client, url) == ["Delta Phone", "Beta Phone", "Alpha Phone"]


# ---------------------------------------------------------------- pagination
def add_bulk_products(count):
    for i in range(1, count + 1):
        db.session.add(SanPham(TENSPH=f"Bulk {i:02d}", HINHANH="no-image.jpg", DONGIA=1000 + i,
                               MOTA="bulk", SOLUONGTON=1, TRANGTHAISPH=1, MADANHMUC=12))
    db.session.commit()


def test_pagination_pages(client, app):
    add_bulk_products(9)  # 9 sản phẩm khớp "bulk", mỗi trang 8 sản phẩm

    assert len(get_names(client, "/products?q=bulk&page=1")) == 8
    assert get_names(client, "/products?q=bulk&page=2") == ["Bulk 09"]


def test_pagination_keeps_all_query_params(client, app):
    add_bulk_products(9)

    page = client.get(
        "/products?q=bulk&category=12&min_price=100&max_price=99999&sort=price_asc&page=1"
    ).get_data(as_text=True)
    page2_link = next(h for h in re.findall(r'href="(/products\?[^"]*)"', page) if "page=2" in h)
    query = parse_qs(urlparse(html.unescape(page2_link)).query)

    assert query["page"] == ["2"]
    assert query["q"] == ["bulk"]
    assert query["category"] == ["12"]
    assert query["min_price"] == ["100"]
    assert query["max_price"] == ["99999"]
    assert query["sort"] == ["price_asc"]


def test_invalid_or_out_of_range_page_does_not_crash(client):
    for page in ("abc", "0", "-3", "999"):
        assert client.get(f"/products?page={page}").status_code == 200, page


# ---------------------------------------------------------------- chi tiết sản phẩm
def test_product_detail_ok(client):
    response = client.get("/products/1")
    assert response.status_code == 200

    page = response.get_data(as_text=True)
    assert "Alpha Phone" in page
    assert "22,000,000" in page
    assert "Phone" in page  # tên danh mục
    assert "/cart/add/1" in page  # còn hàng thì có nút thêm vào giỏ


def test_product_detail_not_found_returns_404(client):
    response = client.get("/products/9999")
    assert response.status_code == 404
    assert "Không tìm thấy sản phẩm" in response.get_data(as_text=True)


def test_inactive_product_detail_returns_404(client):
    assert client.get("/products/5").status_code == 404


def test_out_of_stock_product_cannot_be_added_to_cart(client):
    page = client.get("/products/4").get_data(as_text=True)

    assert "Hết hàng" in page
    assert "/cart/add/4" not in page
    assert "disabled" in page


def test_out_of_stock_badge_on_list(client):
    page = client.get("/products").get_data(as_text=True)
    assert "/cart/add/4" not in page  # Delta Phone hết hàng: không có form thêm vào giỏ
    assert "/cart/add/1" in page


def test_product_detail_back_link_keeps_filters(client):
    page = client.get(
        "/products/1?back_page=2&back_category=11&back_q=alpha&back_sort=newest&back_min_price=100"
    ).get_data(as_text=True)
    back = next(h for h in re.findall(r'href="(/products\?[^"]*)"', page))
    query = parse_qs(urlparse(html.unescape(back)).query)

    assert query["page"] == ["2"]
    assert query["category"] == ["11"]
    assert query["q"] == ["alpha"]
    assert query["sort"] == ["newest"]
    assert query["min_price"] == ["100"]


# ---------------------------------------------------------------- hình ảnh
def test_real_image_url_is_used(client):
    page = client.get("/products/1").get_data(as_text=True)
    assert 'src="https://example.com/alpha.jpg"' in page


def test_missing_or_invalid_image_uses_fallback(client):
    # Sản phẩm 2: "no-image.jpg" (không phải link), sản phẩm 3: None
    for product_id in (2, 3):
        page = client.get(f"/products/{product_id}").get_data(as_text=True)
        assert 'src="/static/img/no-image.svg"' in page, product_id


def test_fallback_image_file_is_served(client):
    response = client.get("/static/img/no-image.svg")
    assert response.status_code == 200


# ---------------------------------------------------------------- product_service
def test_service_get_products_only_active(app):
    pagination = product_service.get_products()
    assert pagination.total == 4
    assert "Hidden Phone" not in [p.TENSPH for p in pagination.items]


def test_service_get_product_by_id(app):
    assert product_service.get_product_by_id(1).TENSPH == "Alpha Phone"
    assert product_service.get_product_by_id(9999) is None
    assert product_service.get_product_by_id(5) is None  # Inactive
    assert product_service.get_product_by_id(5, active_only=False).TENSPH == "Hidden Phone"


def test_service_get_categories(app):
    assert [c.MADANHMUC for c in product_service.get_categories()] == [11, 12, 13]


def test_service_is_available(app):
    alpha = db.session.get(SanPham, 1)       # Active, tồn 10
    delta = db.session.get(SanPham, 4)       # Active, tồn 0
    hidden = db.session.get(SanPham, 5)      # Inactive, tồn 9

    assert product_service.is_available(alpha) is True
    assert product_service.is_available(alpha, 10) is True
    assert product_service.is_available(alpha, 11) is False
    assert product_service.is_available(delta) is False
    assert product_service.is_available(hidden) is False
    assert product_service.is_available(None) is False


def test_service_parse_price():
    from decimal import Decimal

    assert product_service.parse_price("100") == Decimal("100")
    assert product_service.parse_price(" 1500000 ") == Decimal("1500000")
    assert product_service.parse_price("12.5") == Decimal("12.5")
    for bad in (None, "", "  ", "abc", "-5", "1e5", "12.345", "9" * 30):
        assert product_service.parse_price(bad) is None, bad


def test_category_navigation_in_header_and_home(client):
    home_html = client.get("/").get_data(as_text=True)
    assert "Danh Mục Nổi Bật" in home_html
    assert "/products?category=11" in home_html
    assert "/products?category=12" in home_html

    products_html = client.get("/products").get_data(as_text=True)
    assert "Danh mục" in products_html
    assert "/products?category=11" in products_html
    assert "/products?category=12" in products_html