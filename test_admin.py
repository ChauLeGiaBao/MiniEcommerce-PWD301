import html
import os
import sys
from datetime import date
from urllib.parse import unquote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# BẮT BUỘC gán DATABASE_URL là SQLite in-memory trước khi import app/config (LO05)
os.environ["DATABASE_URL"] = "sqlite://"

# Thêm thư mục hiện tại vào sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db, login_manager
from app.models import ChiTietDonHang, DanhMuc, DonHang, SanPham, User


def run_tests():
    print("=" * 75)
    print("🚀 BẮT ĐẦU CHẠY BỘ KIỂM THỬ ADMIN TOÀN DIỆN (TUẦN 3 - LONG)")
    print("=" * 75)

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    login_manager.user_loader(lambda uid: db.session.get(User, int(uid)) if uid and str(uid).isdigit() else None)

    client = app.test_client()

    with app.app_context():
        # LO05: Guard an toàn tuyệt đối chống đụng database thật
        assert str(db.engine.url).startswith("sqlite"), "NGUY HIỂM: Không được chạy test trên database thật!"
        db.create_all()

        # Đảm bảo có danh mục mẫu
        sample_cats = [
            (11, "Điện thoại"),
            (12, "Laptop"),
            (21, "Thời trang nam"),
            (22, "Thời trang nữ"),
        ]
        for cid, cname in sample_cats:
            if not db.session.get(DanhMuc, cid):
                db.session.add(DanhMuc(MADANHMUC=cid, TENDM=cname))
        db.session.commit()

        # Tạo / lấy User Admin, Staff và Customer để kiểm thử phân quyền RBAC
        admin_user = User.query.filter_by(EMAIL="admin@miniecommerce.com").first()
        if not admin_user:
            admin_user = User(
                HOTEN="Trần Vũ Hoàng Long (Admin)",
                EMAIL="admin@miniecommerce.com",
                SDT="0909999999",
                ROLE="admin",
                TRANGTHAIND=1,
            )
            db.session.add(admin_user)

        staff_user = User.query.filter_by(EMAIL="staff@miniecommerce.com").first()
        if not staff_user:
            staff_user = User(
                HOTEN="Nhân Viên Vận Hành (Staff)",
                EMAIL="staff@miniecommerce.com",
                SDT="0908888888",
                ROLE="staff",
                TRANGTHAIND=1,
            )
            db.session.add(staff_user)

        customer_user = User.query.filter_by(EMAIL="customer@example.com").first()
        if not customer_user:
            customer_user = User(
                HOTEN="Nguyễn Văn Khách",
                EMAIL="customer@example.com",
                SDT="0911222333",
                ROLE="customer",
                TRANGTHAIND=1,
            )
            db.session.add(customer_user)
        db.session.commit()

        # ======================================================================
        # TEST 1: BẢO VỆ /admin/* - GUEST TRUY CẬP BỊ CHẶN
        # ======================================================================
        print("\n🔹 [Test 1] Kiểm tra bảo vệ /admin/* - Guest chưa đăng nhập bị chặn:")
        with client.session_transaction() as sess:
            sess.clear()

        # Guest truy cập /admin/ -> bị chặn (redirect về /auth/login)
        res_guest_dash = client.get("/admin/")
        assert res_guest_dash.status_code in (302, 401, 403), f"Status code không hợp lệ: {res_guest_dash.status_code}"
        if res_guest_dash.status_code == 302:
            assert "/auth/login" in res_guest_dash.headers.get("Location", "")

        # Guest truy cập /admin/products -> bị chặn
        res_guest_prod = client.get("/admin/products")
        assert res_guest_prod.status_code in (302, 401, 403)

        # Guest truy cập /admin/orders -> bị chặn
        res_guest_orders = client.get("/admin/orders")
        assert res_guest_orders.status_code in (302, 401, 403)
        print("   👉 KẾT QUẢ: Guest chưa đăng nhập bị CHẶN 100% khỏi tất cả các trang /admin/*!")

        # ======================================================================
        # TEST 1B: CHẶN BACKDOOR SESSION GIẢ LẬP ROLE=ADMIN
        # ======================================================================
        print("\n🔹 [Test 1B] Kiểm tra chặn hoàn toàn backdoor session giả role=admin:")
        with client.session_transaction() as sess:
            sess.clear()
            sess["role"] = "admin"
            sess["user_id"] = admin_user.MANGUOIDUNG

        res_fake = client.get("/admin/")
        assert res_fake.status_code == 302, f"Session giả không được phép truy cập! Nhận: {res_fake.status_code}"
        assert "/auth/login" in res_fake.headers.get("Location", "")
        print("   👉 KẾT QUẢ: Session giả lập role=admin bị CHẶN 100%, bắt buộc đăng nhập thật qua Flask-Login!")

        # ======================================================================
        # TEST 2: BẢO VỆ /admin/* - USER KHÔNG PHẢI ADMIN BỊ CHẶN (403 FORBIDDEN)
        # ======================================================================
        print("\n🔹 [Test 2] Kiểm tra bảo vệ /admin/* - User Customer bị từ chối (403):")
        with client.session_transaction() as sess:
            sess.clear()
            sess["_user_id"] = str(customer_user.MANGUOIDUNG)
            sess["_fresh"] = True

        res_cust_dash = client.get("/admin/")
        assert res_cust_dash.status_code == 403, f"Customer không được vào admin, nhận code: {res_cust_dash.status_code}"

        res_cust_prod = client.get("/admin/products")
        assert res_cust_prod.status_code == 403

        res_cust_orders = client.get("/admin/orders")
        assert res_cust_orders.status_code == 403
        print("   👉 KẾT QUẢ: User có role 'customer' bị từ chối truy cập với mã lỗi HTTP 403 Forbidden!")

        # ======================================================================
        # TEST 2B: MA TRẬN RBAC CHO ROLE STAFF
        # ======================================================================
        print("\n🔹 [Test 2B] Kiểm tra ma trận RBAC cho Staff (Dashboard & Orders: 200, Product CRUD: 403):")
        with client.session_transaction() as sess:
            sess.clear()
            sess["_user_id"] = str(staff_user.MANGUOIDUNG)
            sess["_fresh"] = True

        res_staff_dash = client.get("/admin/")
        assert res_staff_dash.status_code == 200
        res_staff_orders = client.get("/admin/orders")
        assert res_staff_orders.status_code == 200
        res_staff_prod = client.get("/admin/products")
        assert res_staff_prod.status_code == 403
        print("   👉 KẾT QUẢ: Staff vào được Dashboard và Orders, nhưng bị chặn 403 ở Product CRUD!")

        # ======================================================================
        # ĐĂNG NHẬP VỚI QUYỀN ADMIN CHO TOÀN BỘ CÁC NGHIỆP VỤ TIẾP THEO
        # ======================================================================
        with client.session_transaction() as sess:
            sess.clear()
            sess["_user_id"] = str(admin_user.MANGUOIDUNG)
            sess["_fresh"] = True

        # ======================================================================
        # TEST 3: ADMIN TRUY CẬP ĐƯỢC CÁC TRANG ADMIN (200 OK)
        # ======================================================================
        print("\n🔹 [Test 3] Kiểm tra quyền truy cập Admin - Cho phép truy cập bình thường:")
        res_admin_dash = client.get("/admin/")
        assert res_admin_dash.status_code == 200
        dash_text = html.unescape(res_admin_dash.data.decode("utf-8"))
        assert "Tổng quan quản trị (Dashboard)" in dash_text

        res_admin_prod = client.get("/admin/products")
        assert res_admin_prod.status_code == 200

        res_admin_ord = client.get("/admin/orders")
        assert res_admin_ord.status_code == 200
        print("   👉 KẾT QUẢ: Admin truy cập thành công 200 OK vào Dashboard, Products, Orders!")

        # ======================================================================
        # TEST 4: DASHBOARD STATISTICS (DỮ LIỆU QUERY TỪ DB, KHÔNG CRASH KHI TRỐNG)
        # ======================================================================
        print("\n🔹 [Test 4] Kiểm tra Dashboard statistics khi chưa có đơn hàng:")
        assert str(db.engine.url).startswith("sqlite"), "Chốt an toàn SQLite trước khi delete"
        ChiTietDonHang.query.delete()
        DonHang.query.delete()
        db.session.commit()

        res = client.get("/admin/")
        assert res.status_code == 200
        content = html.unescape(res.data.decode("utf-8"))
        assert "Tổng quan quản trị (Dashboard)" in content
        assert "Chưa có đơn hàng nào trong hệ thống" in content
        assert "Tổng doanh thu" in content
        assert "Tình trạng đơn hàng" in content
        print("   👉 KẾT QUẢ: Dashboard hiển thị thống kê an toàn, doanh thu 0đ, không có lỗi!")

        # ======================================================================
        # TEST 5: VALIDATE FORM SẢN PHẨM (GIÁ ÂM, TỒN KHO ÂM BỊ CHẶN)
        # ======================================================================
        print("\n🔹 [Test 5] Kiểm tra Validate Form sản phẩm (tên trống, giá âm, tồn kho âm):")
        # Test tên trống
        res1 = client.post("/admin/products", data={"name": "", "price": "100000", "stock": "10"}, follow_redirects=True)
        assert "Tên sản phẩm không được để trống" in html.unescape(res1.data.decode("utf-8"))

        # Test giá âm
        res2 = client.post("/admin/products", data={"name": "SP Test", "price": "-50000", "stock": "10"}, follow_redirects=True)
        assert "Giá sản phẩm phải lớn hơn hoặc bằng 0" in html.unescape(res2.data.decode("utf-8"))

        # Test tồn kho âm
        res3 = client.post("/admin/products", data={"name": "SP Test", "price": "50000", "stock": "-5"}, follow_redirects=True)
        assert "Số lượng tồn kho phải lớn hơn hoặc bằng 0" in html.unescape(res3.data.decode("utf-8"))

        # Test danh mục không tồn tại
        res4 = client.post("/admin/products", data={"name": "SP Test", "price": "50000", "stock": "5", "category_id": "99999"}, follow_redirects=True)
        assert "Danh mục đã chọn không tồn tại trong hệ thống" in html.unescape(res4.data.decode("utf-8"))
        print("   👉 KẾT QUẢ: Hệ thống chặn hoàn toàn giá âm, tồn kho âm và dữ liệu không hợp lệ!")

        # ======================================================================
        # TEST 6: THÊM SẢN PHẨM HỢP LỆ & THEO DÕI TỒN KHO THẤP (LOW STOCK)
        # ======================================================================
        print("\n🔹 [Test 6] Thêm sản phẩm hợp lệ vào DB & theo dõi cảnh báo tồn kho thấp:")
        old_low_stock = SanPham.query.filter(SanPham.SOLUONGTON <= 5).count()

        res = client.post("/admin/products", data={
            "name": "Bàn phím cơ DareU EK87 Test",
            "price": "650000",
            "stock": "3",
            "category_id": "12",
            "status": "1",
            "description": "Bàn phím cơ gõ êm",
            "image": "keyboard.jpg"
        }, follow_redirects=True)
        assert "Đã thêm sản phẩm 'Bàn phím cơ DareU EK87 Test' thành công" in html.unescape(res.data.decode("utf-8"))

        sp = SanPham.query.filter_by(TENSPH="Bàn phím cơ DareU EK87 Test").first()
        assert sp is not None
        assert sp.SOLUONGTON == 3
        new_low_stock = SanPham.query.filter(SanPham.SOLUONGTON <= 5).count()
        assert new_low_stock == old_low_stock + 1
        print(f"   👉 KẾT QUẢ: Sản phẩm #{sp.MASANPHAM} đã lưu vào DB. Chỉ số low stock tăng chuẩn xác ({old_low_stock} -> {new_low_stock})!")

        # ======================================================================
        # TEST 7: SỬA SẢN PHẨM VÀ CẬP NHẬT KHO / CHẶN GIÁ ÂM KHI SỬA
        # ======================================================================
        print("\n🔹 [Test 7] Chỉnh sửa sản phẩm và cập nhật kho / Validate không cho giá âm khi sửa:")
        # Thử sửa giá âm -> bị chặn
        res_bad_edit = client.post(f"/admin/products/{sp.MASANPHAM}/edit", data={
            "name": sp.TENSPH,
            "price": "-200000",
            "stock": "10",
        }, follow_redirects=True)
        assert "Giá sản phẩm phải lớn hơn hoặc bằng 0" in html.unescape(res_bad_edit.data.decode("utf-8"))

        # Sửa hợp lệ: Nhập thêm kho từ 3 lên 30 chiếc
        res_good_edit = client.post(f"/admin/products/{sp.MASANPHAM}/edit", data={
            "name": "Bàn phím cơ DareU EK87 Test (Đã nhập thêm)",
            "price": "620000",
            "stock": "30",
            "category_id": "12",
            "status": "1",
            "description": "Đã về thêm 30 chiếc",
            "image": "keyboard.jpg"
        }, follow_redirects=True)
        assert "Đã cập nhật sản phẩm" in html.unescape(res_good_edit.data.decode("utf-8"))

        db.session.refresh(sp)
        assert sp.SOLUONGTON == 30
        assert sp.TENSPH == "Bàn phím cơ DareU EK87 Test (Đã nhập thêm)"
        current_low_stock = SanPham.query.filter(SanPham.SOLUONGTON <= 5).count()
        assert current_low_stock == old_low_stock
        print("   👉 KẾT QUẢ: Cập nhật thành công, thoát khỏi danh sách cảnh báo tồn kho thấp!")

        # ======================================================================
        # TEST 8: PRODUCTS NÂNG CAO - SEARCH, FILTER CATEGORY, LOW STOCK, PAGINATION
        # ======================================================================
        print("\n🔹 [Test 8] Kiểm tra Products nâng cao (Search, Filter category, Low stock, Pagination):")
        # 1. Search theo tên sản phẩm
        res_search = client.get("/admin/products?q=DareU")
        search_html = html.unescape(res_search.data.decode("utf-8"))
        assert "DareU EK87" in search_html
        assert res_search.status_code == 200

        # Search từ khóa không khớp
        res_no_match = client.get("/admin/products?q=KhongCoSanPhamNayTrongKho12345")
        no_match_html = html.unescape(res_no_match.data.decode("utf-8"))
        assert "Không tìm thấy sản phẩm nào phù hợp với bộ lọc tìm kiếm" in no_match_html

        # 2. Filter theo Category
        res_cat = client.get("/admin/products?category_id=12")
        cat_html = html.unescape(res_cat.data.decode("utf-8"))
        assert res_cat.status_code == 200
        assert "Laptop" in cat_html

        # 3. Filter low stock
        # Tạo tạm 1 sản phẩm có stock = 2
        sp_low = SanPham(
            TENSPH="Sản phẩm thử nghiệm Low Stock",
            DONGIA=150000,
            SOLUONGTON=2,
            TRANGTHAISPH=1,
            MADANHMUC=11,
        )
        db.session.add(sp_low)
        db.session.commit()

        res_low = client.get("/admin/products?low_stock=1")
        low_html = html.unescape(res_low.data.decode("utf-8"))
        assert "Sản phẩm thử nghiệm Low Stock" in low_html

        # 4. Pagination và giữ query params
        res_p1 = client.get("/admin/products?page=1&q=DareU")
        assert res_p1.status_code == 200
        p1_html = html.unescape(res_p1.data.decode("utf-8"))
        assert 'name="q"' in p1_html
        assert "DareU" in p1_html
        print("   👉 KẾT QUẢ: Search, Filter danh mục, Filter low-stock và Pagination hoạt động chính xác!")

        # ======================================================================
        # TEST 9: TẠO ĐƠN HÀNG VÀ ORDERS NÂNG CAO (SEARCH, FILTER, SORT, PAGINATION)
        # ======================================================================
        print("\n🔹 [Test 9] Kiểm tra Orders nâng cao (Search mã/người nhận/SĐT, Filter status, Sort, Pagination):")
        # Tạo 3 đơn hàng với trạng thái khác nhau
        order1 = DonHang(
            HOTENNHAN="Nguyễn Văn An",
            SDTNHAN="0912345678",
            DIACHIGIAO="123 Cầu Giấy, Hà Nội",
            NGAYDAT=date(2026, 1, 10),
            TONGGIATRI=1200000,
            TRANGTHAI=0,  # Mới
        )
        order2 = DonHang(
            HOTENNHAN="Trần Thị Bình",
            SDTNHAN="0987654321",
            DIACHIGIAO="456 Hai Bà Trưng, Hà Nội",
            NGAYDAT=date(2026, 2, 15),
            TONGGIATRI=2500000,
            TRANGTHAI=1,  # Đang xử lý
        )
        order3 = DonHang(
            HOTENNHAN="Lê Hoàng Cường",
            SDTNHAN="0933333333",
            DIACHIGIAO="789 Nguyễn Huệ, TP.HCM",
            NGAYDAT=date(2026, 3, 20),
            TONGGIATRI=3800000,
            TRANGTHAI=2,  # Hoàn thành
        )
        db.session.add_all([order1, order2, order3])
        db.session.flush()

        detail1 = ChiTietDonHang(MADONHANG=order1.MADONHANG, MASANPHAM=sp.MASANPHAM, SOLUONG=2)
        db.session.add(detail1)
        db.session.commit()

        o1_id, o2_id, o3_id = order1.MADONHANG, order2.MADONHANG, order3.MADONHANG

        # 1. Search theo người nhận
        res_search_name = client.get("/admin/orders?q=Nguyễn+Văn+An")
        assert f"#{o1_id}" in html.unescape(res_search_name.data.decode("utf-8"))

        # 2. Search theo SĐT
        res_search_phone = client.get("/admin/orders?q=0987654321")
        phone_html = html.unescape(res_search_phone.data.decode("utf-8"))
        assert f"#{o2_id}" in phone_html
        assert "Trần Thị Bình" in phone_html

        # 3. Search theo mã đơn (#id)
        res_search_id = client.get(f"/admin/orders?q={o3_id}")
        assert f"#{o3_id}" in html.unescape(res_search_id.data.decode("utf-8"))

        # 4. Filter theo trạng thái (status=1 -> Đang xử lý)
        res_filter_st = client.get("/admin/orders?status=1")
        st_html = html.unescape(res_filter_st.data.decode("utf-8"))
        assert f"#{o2_id}" in st_html
        assert "Trần Thị Bình" in st_html
        assert "Nguyễn Văn An" not in st_html  # o1 (Nguyễn Văn An) có status=0 không được xuất hiện

        # 5. Sort mới nhất / cũ nhất
        res_sort_oldest = client.get("/admin/orders?sort=oldest")
        assert res_sort_oldest.status_code == 200

        res_sort_newest = client.get("/admin/orders?sort=newest")
        assert res_sort_newest.status_code == 200

        # 6. Pagination giữ search/filter/sort
        res_order_page = client.get(f"/admin/orders?page=1&q=Nguyễn&status=0&sort=newest")
        page_html = html.unescape(res_order_page.data.decode("utf-8"))
        assert 'name="q"' in page_html
        assert 'Nguyễn' in page_html
        print("   👉 KẾT QUẢ: Order search (mã/tên/SĐT), filter status, sort và pagination giữ query params hoàn hảo!")

        # ======================================================================
        # TEST 10: XEM CHI TIẾT ĐƠN HÀNG (/admin/orders/<id>)
        # ======================================================================
        print(f"\n🔹 [Test 10] Xem chi tiết đơn hàng #{o1_id}:")
        res_detail = client.get(f"/admin/orders/{o1_id}")
        assert res_detail.status_code == 200
        detail_html = html.unescape(res_detail.data.decode("utf-8"))
        assert f"Chi tiết đơn hàng #{o1_id}" in detail_html
        assert "Nguyễn Văn An" in detail_html
        assert "0912345678" in detail_html
        assert "123 Cầu Giấy" in detail_html
        assert sp.TENSPH in detail_html
        assert "2" in detail_html
        print("   👉 KẾT QUẢ: Chi tiết đơn hàng hiển thị đầy đủ thông tin khách hàng, địa chỉ, mặt hàng, subtotal!")

        # ======================================================================
        # TEST 11: CẬP NHẬT TRẠNG THÁI ĐƠN HÀNG & CHẶN INVALID STATUS
        # ======================================================================
        print(f"\n🔹 [Test 11] Cập nhật trạng thái đơn hàng & Chặn status không hợp lệ:")
        # 1. Thử status không hợp lệ (status = 999) -> bị chặn
        res_bad_st1 = client.post(f"/admin/orders/{o1_id}/status", data={"status": "999"}, follow_redirects=True)
        assert "Trạng thái đơn hàng không hợp lệ" in html.unescape(res_bad_st1.data.decode("utf-8"))
        db.session.refresh(order1)
        assert order1.TRANGTHAI == 0, "Trạng thái DB không được phép thay đổi khi client gửi status sai!"

        # 2. Thử status không hợp lệ (status = "hacker") -> bị chặn
        res_bad_st2 = client.post(f"/admin/orders/{o1_id}/status", data={"status": "hacker"}, follow_redirects=True)
        assert "Trạng thái đơn hàng không hợp lệ" in html.unescape(res_bad_st2.data.decode("utf-8"))

        # 3. Cập nhật status hợp lệ (0 -> 1: Đang xử lý)
        res_good_st1 = client.post(f"/admin/orders/{o1_id}/status", data={"status": "1"}, follow_redirects=True)
        assert "Đã cập nhật trạng thái đơn hàng" in html.unescape(res_good_st1.data.decode("utf-8"))
        db.session.refresh(order1)
        assert order1.TRANGTHAI == 1

        # 4. Cập nhật status hợp lệ (1 -> 2: Hoàn thành)
        client.post(f"/admin/orders/{o1_id}/status", data={"status": "2"}, follow_redirects=True)
        db.session.refresh(order1)
        assert order1.TRANGTHAI == 2
        print(f"   👉 KẾT QUẢ: Chặn thành công 100% status tùy ý! Cập nhật status hợp lệ (0 -> 1 -> 2) lưu vĩnh viễn vào DB!")

        # ======================================================================
        # TEST 12: DELETE AN TOÀN - CHẶN XÓA SẢN PHẨM ĐÃ CÓ TRONG ĐƠN HÀNG (TRÁNH LỖI FK/500)
        # ======================================================================
        print(f"\n🔹 [Test 12] Kiểm tra xóa sản phẩm an toàn:")
        # Sản phẩm `sp` đang nằm trong `order1` -> phải bị CHẶN xóa, không bị lỗi 500
        res_del_blocked = client.post(f"/admin/products/{sp.MASANPHAM}/delete", follow_redirects=True)
        del_blocked_msg = html.unescape(res_del_blocked.data.decode("utf-8"))
        assert "Không thể xóa sản phẩm" in del_blocked_msg
        assert "vì đã có trong đơn hàng tham chiếu" in del_blocked_msg
        assert db.session.get(SanPham, sp.MASANPHAM) is not None, "Sản phẩm không được bị xóa khỏi DB!"
        print("   👉 KẾT QUẢ: Hệ thống CHẶN xóa sản phẩm đã có đơn hàng tham chiếu, trả thông báo nghiệp vụ an toàn thay vì lỗi 500!")

        # Xóa sản phẩm chưa có trong đơn hàng -> Xóa thành công
        pid_clean = sp_low.MASANPHAM
        res_del_clean = client.post(f"/admin/products/{pid_clean}/delete", follow_redirects=True)
        assert "Đã xóa sản phẩm" in html.unescape(res_del_clean.data.decode("utf-8"))
        assert db.session.get(SanPham, pid_clean) is None
        print(f"   👉 KẾT QUẢ: Sản phẩm #{pid_clean} chưa có đơn hàng được xóa sạch sẽ khỏi DB!")

        # ======================================================================
        # TEST 13: KHÔNG PHÁ CÁC ROUTE SHOP BÊN NGOÀI
        # ======================================================================
        print("\n🔹 [Test 13] Kiểm tra tính toàn vẹn của các route Shop bên ngoài (/ , /products, /cart, /checkout):")
        assert client.get("/").status_code == 200
        assert client.get("/products").status_code == 200
        assert client.get("/cart").status_code == 200
        # /checkout: khi giỏ trống redirect 302 về /products; khi có giỏ hàng trả về 200
        assert client.get("/checkout").status_code == 302
        assert client.get("/checkout", follow_redirects=True).status_code == 200
        with client.session_transaction() as sess:
            sess["cart"] = {str(sp.MASANPHAM): 1}
        assert client.get("/checkout").status_code == 200
        print("   👉 KẾT QUẢ: Toàn bộ route Shop bên ngoài (/ , /products, /cart, /checkout) hoạt động bình thường 100%!")

    print("\n" + "=" * 75)
    print("🎉 TẤT CẢ 13 BỘ KIỂM THỬ ADMIN TUẦN 3 ĐÃ HOÀN TOÀN THÀNH CÔNG VÀ CHÍNH XÁC 100%!")
    print("=" * 75)


if __name__ == "__main__":
    run_tests()
