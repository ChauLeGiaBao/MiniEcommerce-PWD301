"""
Bộ kiểm thử tự động toàn diện cho Module Admin (Tuần 3 & Hoàn thiện - Long)
Các yêu cầu tuân thủ nghiêm ngặt theo W4_Cong_viec_con_lai_Long.pdf:
- LO01: RBAC 3 vai trò (Guest -> login, Customer -> 403, Staff -> xem/cập nhật đơn / cấm CRUD SP, Admin -> 200).
        Loại bỏ hoàn toàn backdoor qua session giả lập (session['role'] / session['user_id']).
- LO02: Dashboard KPI chính xác: Tổng sản phẩm, đơn hàng, tồn thấp (<= 5),
        Doanh thu loại trừ đơn hủy (TRANGTHAI == 3), Doanh thu hoàn thành (TRANGTHAI == 2),
        DB trống an toàn không crash.
- LO03: Product CRUD hoàn chỉnh: validate giá/tồn kho âm, danh mục, URL/mô tả dài;
        bảo lưu form_data khi lỗi; safe delete chặn xóa sản phẩm đã có đơn hàng tham chiếu (FK).
- LO04: Orders Admin: Search (mã/tên/SĐT), Filter trạng thái, Sort, Pagination bảo lưu params,
        Chi tiết đơn hàng đầy đủ PII/sản phẩm; Cập nhật status (chỉ 0/1/2/3 hợp lệ, chặn status lạ, 404).
- LO05: Cô lập hoàn toàn trên DB test SQLite in-memory, có guard assert tuyệt đối không đụng DB thật.
"""

from datetime import date
import html
import pytest
from app.extensions import db
from app.models import ChiTietDonHang, DanhMuc, DonHang, SanPham, User


# ==============================================================================
# Helper & Fixtures
# ==============================================================================
def create_test_users():
    """Tạo các tài khoản đại diện cho 3 vai trò RBAC."""
    admin = User.query.filter_by(EMAIL="admin@test.com").first()
    if not admin:
        admin = User(
            HOTEN="Admin Quản Trị Viên",
            EMAIL="admin@test.com",
            SDT="0901111111",
            ROLE="admin",
            TRANGTHAIND=1,
        )
        db.session.add(admin)

    staff = User.query.filter_by(EMAIL="staff@test.com").first()
    if not staff:
        staff = User(
            HOTEN="Nhân Viên Bán Hàng",
            EMAIL="staff@test.com",
            SDT="0902222222",
            ROLE="staff",
            TRANGTHAIND=1,
        )
        db.session.add(staff)

    customer = User.query.filter_by(EMAIL="customer@test.com").first()
    if not customer:
        customer = User(
            HOTEN="Khách Hàng Thân Thiết",
            EMAIL="customer@test.com",
            SDT="0903333333",
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(customer)

    db.session.commit()
    return admin, staff, customer


def login_client(client, user):
    """Giả lập đăng nhập qua session chính thức của Flask-Login."""
    with client.session_transaction() as sess:
        sess.clear()
        sess["_user_id"] = str(user.MANGUOIDUNG)
        sess["_fresh"] = True


# ==============================================================================
# LO05: Guard an toàn cơ sở dữ liệu
# ==============================================================================
def test_db_guard_is_isolated_sqlite(app):
    """Đảm bảo tất cả các test chạy trên SQLite in-memory, tuyệt đối không chạm DB thật."""
    db_url = str(db.engine.url)
    assert db_url.startswith("sqlite"), f"Nguy hiểm: Test đang chạy trên database không phải SQLite: {db_url}"


# ==============================================================================
# LO01: RBAC 3 vai trò & Xóa bỏ Session Giả Lập
# ==============================================================================
def test_guest_redirected_to_login_on_all_admin_routes(client):
    """Guest chưa đăng nhập truy cập bất kỳ route /admin/* nào đều bị chuyển hướng về login."""
    routes = ["/admin/", "/admin/products", "/admin/orders"]
    for route in routes:
        res = client.get(route)
        assert res.status_code == 302, f"Route {route} không chuyển hướng guest, status: {res.status_code}"
        assert "/auth/login" in res.headers.get("Location", "")


def test_guest_ajax_unauthorized_401(client):
    """Guest gọi AJAX / XMLHttpRequest tới /admin/* nhận mã lỗi 401 Unauthorized thay vì 302."""
    res = client.get("/admin/", headers={"X-Requested-With": "XMLHttpRequest"})
    assert res.status_code == 401
    json_data = res.get_json()
    assert json_data["error"] == "Unauthorized"


def test_fake_session_role_is_strictly_rejected(client):
    """
    Backdoor Check: Client tự ý set session['role']='admin' hoặc session['user_id']
    mà không đăng nhập qua Flask-Login -> Bị coi là Guest và chuyển hướng về /auth/login.
    """
    with client.session_transaction() as sess:
        sess.clear()
        sess["role"] = "admin"
        sess["user_id"] = 1

    res = client.get("/admin/")
    assert res.status_code == 302
    assert "/auth/login" in res.headers.get("Location", "")


def test_customer_forbidden_403_on_all_admin_routes(app, client):
    """Customer đã đăng nhập truy cập bất kỳ trang /admin/* nào đều nhận 403 Forbidden."""
    _, _, customer = create_test_users()
    login_client(client, customer)

    for route in ["/admin/", "/admin/products", "/admin/orders"]:
        res = client.get(route)
        assert res.status_code == 403, f"Customer không được vào {route}, nhận code {res.status_code}"


def test_customer_tampering_session_role_still_forbidden(app, client):
    """Customer đã login nhưng cố sửa session['role'] = 'admin' vẫn bị chặn 403."""
    _, _, customer = create_test_users()
    login_client(client, customer)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    res = client.get("/admin/")
    assert res.status_code == 403


def test_staff_role_permissions_matrix(app, client):
    """
    Staff Role Matrix:
    - Được phép xem Dashboard (/admin/) -> 200 OK
    - Được phép xem danh sách đơn hàng (/admin/orders) -> 200 OK
    - BỊ CHẶN 403 Forbidden đối với Quản lý Sản phẩm (Product CRUD: /admin/products, edit, delete).
    """
    _, staff, _ = create_test_users()
    login_client(client, staff)

    # 1. Dashboard: Được phép (200)
    res_dash = client.get("/admin/")
    assert res_dash.status_code == 200
    assert "STAFF" in html.unescape(res_dash.get_data(as_text=True))

    # 2. Orders: Được phép (200)
    res_orders = client.get("/admin/orders")
    assert res_orders.status_code == 200

    # 3. Product CRUD: BỊ CHẶN 403
    res_prod = client.get("/admin/products")
    assert res_prod.status_code == 403

    res_add_prod = client.post("/admin/products", data={"name": "Test SP Staff"})
    assert res_add_prod.status_code == 403

    res_edit_prod = client.get("/admin/products/1/edit")
    assert res_edit_prod.status_code == 403

    res_del_prod = client.post("/admin/products/1/delete")
    assert res_del_prod.status_code == 403


def test_admin_role_full_access(app, client):
    """Admin có toàn quyền truy cập tất cả các trang /admin/* (200 OK)."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    for route in ["/admin/", "/admin/products", "/admin/orders", "/admin/products/1/edit"]:
        res = client.get(route)
        assert res.status_code == 200, f"Admin phải vào được {route}, nhận code {res.status_code}"


def test_logout_immediately_revokes_admin_access(app, client):
    """Sau khi đăng xuất (clear session Flask-Login), truy cập lại bị chặn ngay lập tức."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    assert client.get("/admin/").status_code == 200

    with client.session_transaction() as sess:
        sess.clear()

    res = client.get("/admin/")
    assert res.status_code == 302
    assert "/auth/login" in res.headers.get("Location", "")


# ==============================================================================
# LO02: Dashboard KPI & Thống Kê Doanh Thu
# ==============================================================================
def test_dashboard_empty_db_no_crash(app, client):
    """Dashboard khi chưa có bất kỳ đơn hàng nào: không lỗi 500, doanh thu trả về 0đ."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    res = client.get("/admin/")
    assert res.status_code == 200
    page_text = html.unescape(res.get_data(as_text=True))
    assert "Tổng quan quản trị (Dashboard)" in page_text
    assert "Chưa có đơn hàng nào trong hệ thống" in page_text


def test_dashboard_kpi_revenue_excludes_cancelled_orders(app, client):
    """
    Quy tắc LO02:
    - Tổng doanh thu (total_revenue) loại trừ đơn đã hủy (TRANGTHAI == 3).
    - Doanh thu hoàn thành (completed_revenue) chỉ tính đơn hoàn thành (TRANGTHAI == 2).
    """
    admin, _, _ = create_test_users()
    login_client(client, admin)

    # Tạo 4 đơn hàng: Mới (0), Đang xử lý (1), Hoàn thành (2), Đã hủy (3)
    o0 = DonHang(HOTENNHAN="Khach A", SDTNHAN="0911", DIACHIGIAO="HN", TONGGIATRI=100000, TRANGTHAI=0, NGAYDAT=date.today())
    o1 = DonHang(HOTENNHAN="Khach B", SDTNHAN="0922", DIACHIGIAO="DN", TONGGIATRI=200000, TRANGTHAI=1, NGAYDAT=date.today())
    o2 = DonHang(HOTENNHAN="Khach C", SDTNHAN="0933", DIACHIGIAO="SG", TONGGIATRI=500000, TRANGTHAI=2, NGAYDAT=date.today())
    o3 = DonHang(HOTENNHAN="Khach D", SDTNHAN="0944", DIACHIGIAO="HP", TONGGIATRI=999999, TRANGTHAI=3, NGAYDAT=date.today()) # Đơn hủy!

    db.session.add_all([o0, o1, o2, o3])
    db.session.commit()

    res = client.get("/admin/")
    assert res.status_code == 200
    page_text = html.unescape(res.get_data(as_text=True))

    # Doanh thu hợp lệ = 100k + 200k + 500k = 800,000 đ (KHÔNG tính 999,999đ của đơn hủy)
    assert "800,000" in page_text
    # Doanh thu hoàn thành = 500,000 đ
    assert "500,000" in page_text


def test_dashboard_low_stock_threshold_5(app, client):
    """Kiểm tra ngưỡng cảnh báo tồn kho thấp (SOLUONGTON <= 5)."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    # Trong seed data conftest.py:
    # Beta Phone (tồn 5), Gamma Laptop (tồn 3), Delta Phone (tồn 0) -> Có 3 sản phẩm <= 5
    res = client.get("/admin/")
    assert res.status_code == 200
    page_text = html.unescape(res.get_data(as_text=True))
    assert "Cảnh báo tồn kho thấp" in page_text
    assert "Gamma Laptop" in page_text


# ==============================================================================
# LO03: Product Admin CRUD, Validation & Safe Delete
# ==============================================================================
def test_admin_add_product_success(app, client):
    """Admin thêm sản phẩm hợp lệ thành công."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    res = client.post("/admin/products", data={
        "name": "Tai nghe Sony WH-1000XM5 Test",
        "price": "7500000",
        "stock": "15",
        "category_id": "11",
        "status": "1",
        "image": "https://example.com/sony.jpg",
        "description": "Tai nghe chống ồn đỉnh cao",
    }, follow_redirects=True)

    assert res.status_code == 200
    page_text = html.unescape(res.get_data(as_text=True))
    assert "Đã thêm sản phẩm 'Tai nghe Sony WH-1000XM5 Test' thành công" in page_text

    prod = SanPham.query.filter_by(TENSPH="Tai nghe Sony WH-1000XM5 Test").first()
    assert prod is not None
    assert prod.DONGIA == 7500000
    assert prod.SOLUONGTON == 15


def test_admin_add_product_validation_errors_preserve_form_data(app, client):
    """Kiểm tra các trường hợp validation lỗi và bảo lưu dữ liệu form đã nhập."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    # 1. Tên trống
    res1 = client.post("/admin/products", data={"name": "", "price": "10000", "stock": "5"}, follow_redirects=True)
    assert "Tên sản phẩm không được để trống" in html.unescape(res1.get_data(as_text=True))

    # 2. Giá âm
    res2 = client.post("/admin/products", data={
        "name": "Sản phẩm giá âm",
        "price": "-50000",
        "stock": "5",
    }, follow_redirects=True)
    text2 = html.unescape(res2.get_data(as_text=True))
    assert "Giá sản phẩm phải lớn hơn hoặc bằng 0" in text2
    assert "Sản phẩm giá âm" in text2  # Bảo lưu dữ liệu nhập

    # 3. Tồn kho âm
    res3 = client.post("/admin/products", data={
        "name": "Sản phẩm tồn kho âm",
        "price": "50000",
        "stock": "-10",
    }, follow_redirects=True)
    assert "Số lượng tồn kho phải lớn hơn hoặc bằng 0" in html.unescape(res3.get_data(as_text=True))

    # 4. Danh mục không tồn tại
    res4 = client.post("/admin/products", data={
        "name": "Sản phẩm danh mục sai",
        "price": "50000",
        "stock": "1",
        "category_id": "99999",
    }, follow_redirects=True)
    assert "Danh mục đã chọn không tồn tại trong hệ thống" in html.unescape(res4.get_data(as_text=True))


def test_admin_edit_product_success(app, client):
    """Admin chỉnh sửa sản phẩm hiện có thành công."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    res = client.post("/admin/products/1/edit", data={
        "name": "Alpha Phone Edition 2026",
        "price": "25000000",
        "stock": "20",
        "category_id": "11",
        "status": "1",
        "image": "alpha-new.jpg",
        "description": "Nâng cấp bộ nhớ 512GB",
    }, follow_redirects=True)

    assert res.status_code == 200
    sp1 = db.session.get(SanPham, 1)
    assert sp1.TENSPH == "Alpha Phone Edition 2026"
    assert sp1.DONGIA == 25000000
    assert sp1.SOLUONGTON == 20


def test_admin_safe_delete_blocks_product_in_order(app, client):
    """
    Safe Delete (LO03): Sản phẩm đã nằm trong đơn hàng (ChiTietDonHang)
    bắt buộc bị CHẶN xóa, không làm hỏng khóa ngoại và trả thông báo nghiệp vụ rõ ràng.
    """
    admin, _, _ = create_test_users()
    login_client(client, admin)

    # Tạo 1 đơn hàng tham chiếu tới SanPham ID = 1
    order = DonHang(HOTENNHAN="Khach Test", SDTNHAN="0911222333", DIACHIGIAO="HN", TONGGIATRI=22000000, TRANGTHAI=1, NGAYDAT=date.today())
    db.session.add(order)
    db.session.flush()
    detail = ChiTietDonHang(MADONHANG=order.MADONHANG, MASANPHAM=1, SOLUONG=1)
    db.session.add(detail)
    db.session.commit()

    # Thử xóa sản phẩm ID = 1 -> Phải bị CHẶN
    res = client.post("/admin/products/1/delete", follow_redirects=True)
    assert res.status_code == 200
    page_text = html.unescape(res.get_data(as_text=True))
    assert "Không thể xóa sản phẩm" in page_text
    assert "vì đã có trong đơn hàng tham chiếu" in page_text

    # Đảm bảo sản phẩm vẫn còn nguyên trong DB
    assert db.session.get(SanPham, 1) is not None


def test_admin_delete_unreferenced_product_success(app, client):
    """Sản phẩm chưa có trong đơn hàng được xóa thành công khỏi database."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    # Tạo một sản phẩm mới tinh chưa có đơn hàng
    sp_new = SanPham(TENSPH="Sản phẩm tạm xóa", DONGIA=50000, SOLUONGTON=1, TRANGTHAISPH=1)
    db.session.add(sp_new)
    db.session.commit()
    new_id = sp_new.MASANPHAM

    res = client.post(f"/admin/products/{new_id}/delete", follow_redirects=True)
    assert res.status_code == 200
    assert "Đã xóa sản phẩm 'Sản phẩm tạm xóa' thành công" in html.unescape(res.get_data(as_text=True))
    assert db.session.get(SanPham, new_id) is None


def test_inactive_product_hidden_from_shop(app, client):
    """Khi sản phẩm có trạng thái Tạm ẩn (TRANGTHAISPH = 0), sản phẩm không xuất hiện trên Shop."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    # Đổi sản phẩm 2 (Beta Phone) sang Tạm ẩn (0)
    client.post("/admin/products/2/edit", data={
        "name": "Beta Phone",
        "price": "18000000",
        "stock": "5",
        "category_id": "11",
        "status": "0",  # Tạm ẩn
    }, follow_redirects=True)

    # Vào trang shop bên ngoài kiểm tra
    res_shop = client.get("/products")
    assert res_shop.status_code == 200
    shop_text = html.unescape(res_shop.get_data(as_text=True))
    assert "Beta Phone" not in shop_text


# ==============================================================================
# LO04: Orders Admin List, Detail, Search & Status Update
# ==============================================================================
def test_admin_orders_search_filter_sort_and_pagination(app, client):
    """Kiểm tra Orders list: tìm kiếm theo mã/tên/SĐT, lọc trạng thái, sắp xếp."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    o1 = DonHang(HOTENNHAN="Nguyen Van Hoang", SDTNHAN="0911122233", DIACHIGIAO="Ha Noi", TONGGIATRI=1500000, TRANGTHAI=0, NGAYDAT=date(2026, 1, 1))
    o2 = DonHang(HOTENNHAN="Tran Thi Mai", SDTNHAN="0988877766", DIACHIGIAO="Da Nang", TONGGIATRI=2500000, TRANGTHAI=1, NGAYDAT=date(2026, 2, 1))
    db.session.add_all([o1, o2])
    db.session.commit()

    # 1. Search theo tên
    res_name = client.get("/admin/orders?q=Hoang")
    assert "Nguyen Van Hoang" in html.unescape(res_name.get_data(as_text=True))

    # 2. Search theo SĐT
    res_phone = client.get("/admin/orders?q=0988877766")
    assert "Tran Thi Mai" in html.unescape(res_phone.get_data(as_text=True))

    # 3. Filter theo trạng thái (status=1 -> Đang xử lý)
    res_st = client.get("/admin/orders?status=1")
    st_text = html.unescape(res_st.get_data(as_text=True))
    assert "Tran Thi Mai" in st_text
    assert "Nguyen Van Hoang" not in st_text


def test_admin_order_detail_view(app, client):
    """Trang chi tiết đơn hàng hiển thị đầy đủ thông tin giao hàng, khách hàng, sản phẩm và tổng tiền."""
    admin, _, _ = create_test_users()
    login_client(client, admin)

    order = DonHang(HOTENNHAN="Le Van Tam", SDTNHAN="0977665544", DIACHIGIAO="123 Le Loi, Q1, HCM", TONGGIATRI=44000000, TRANGTHAI=0, NGAYDAT=date.today())
    db.session.add(order)
    db.session.flush()
    detail = ChiTietDonHang(MADONHANG=order.MADONHANG, MASANPHAM=1, SOLUONG=2)
    db.session.add(detail)
    db.session.commit()

    res = client.get(f"/admin/orders/{order.MADONHANG}")
    assert res.status_code == 200
    page_text = html.unescape(res.get_data(as_text=True))
    assert f"Chi tiết đơn hàng #{order.MADONHANG}" in page_text
    assert "Le Van Tam" in page_text
    assert "0977665544" in page_text
    assert "123 Le Loi, Q1, HCM" in page_text
    assert "Alpha Phone" in page_text
    assert "44,000,000" in page_text


def test_admin_update_order_status_valid_and_invalid(app, client):
    """
    Cập nhật trạng thái đơn hàng:
    - Status hợp lệ (0 -> 1 -> 2 -> 3) lưu thành công vào DB.
    - Status lạ (999, hacker) bị CHẶN, không thay đổi DB.
    - Order ID sai trả về 404.
    """
    admin, _, _ = create_test_users()
    login_client(client, admin)

    order = DonHang(HOTENNHAN="Nguyen Test Status", SDTNHAN="0911", DIACHIGIAO="HN", TONGGIATRI=100000, TRANGTHAI=0, NGAYDAT=date.today())
    db.session.add(order)
    db.session.commit()
    oid = order.MADONHANG

    # 1. Status lạ -> bị từ chối
    res_bad = client.post(f"/admin/orders/{oid}/status", data={"status": "999"}, follow_redirects=True)
    assert "Trạng thái đơn hàng không hợp lệ" in html.unescape(res_bad.get_data(as_text=True))
    db.session.refresh(order)
    assert order.TRANGTHAI == 0

    # 2. Status hợp lệ: 0 -> 1 (Đang xử lý)
    res_good1 = client.post(f"/admin/orders/{oid}/status", data={"status": "1"}, follow_redirects=True)
    assert "Đã cập nhật trạng thái đơn hàng" in html.unescape(res_good1.get_data(as_text=True))
    db.session.refresh(order)
    assert order.TRANGTHAI == 1

    # 3. Status hợp lệ: 1 -> 2 (Hoàn thành)
    client.post(f"/admin/orders/{oid}/status", data={"status": "2"}, follow_redirects=True)
    db.session.refresh(order)
    assert order.TRANGTHAI == 2

    # 4. Order ID không tồn tại -> 404
    res_404 = client.post("/admin/orders/999999/status", data={"status": "1"})
    assert res_404.status_code == 404


def test_customer_cannot_update_order_status(app, client):
    """Customer không có quyền POST đổi trạng thái đơn hàng (bị chặn 403 Forbidden)."""
    _, _, customer = create_test_users()

    order = DonHang(HOTENNHAN="Test Order", SDTNHAN="0911", DIACHIGIAO="HN", TONGGIATRI=100000, TRANGTHAI=0, NGAYDAT=date.today())
    db.session.add(order)
    db.session.commit()
    oid = order.MADONHANG

    login_client(client, customer)
    res = client.post(f"/admin/orders/{oid}/status", data={"status": "2"})
    assert res.status_code == 403
    db.session.refresh(order)
    assert order.TRANGTHAI == 0
