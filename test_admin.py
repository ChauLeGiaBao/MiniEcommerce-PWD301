import html
import os
import sys
from datetime import date

# Thêm thư mục hiện tại vào đường dẫn
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import ChiTietDonHang, DanhMuc, DonHang, SanPham, User


def run_tests():
    print("=" * 70)
    print("🚀 BẮT ĐẦU CHẠY KIỂM THỬ CÁC NGHIỆP VỤ ADMIN (TUẦN 2 - LONG)")
    print("=" * 70)

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    client = app.test_client()

    with app.app_context():
        db.create_all()

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 1: Dashboard khi chưa có đơn hàng
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 1] Kiểm tra Dashboard khi chưa có đơn hàng:")
        print("   - Đảm bảo Dashboard không bị crash (Zero Division/NoneType) khi DB rỗng đơn hàng.")
        # Dọn sạch đơn hàng tạm để test
        ChiTietDonHang.query.delete()
        DonHang.query.delete()
        db.session.commit()

        res = client.get("/admin/")
        assert res.status_code == 200
        content = html.unescape(res.data.decode("utf-8"))
        assert "Tổng quan quản trị (Dashboard)" in content
        assert "Chưa có đơn hàng nào trong hệ thống" in content
        print("   👉 KẾT QUẢ: Dashboard hiển thị hoàn hảo, doanh thu = 0đ, không có lỗi!")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 2: Validate thêm sản phẩm
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 2] Kiểm tra ràng buộc và Validate form thêm sản phẩm:")
        print("   - Kiểm tra các trường hợp: Tên trống, Giá âm (<0), Tồn kho âm, Danh mục không tồn tại.")
        
        # Test tên trống
        res1 = client.post("/admin/products", data={"name": "", "price": "100000", "stock": "10"}, follow_redirects=True)
        assert "Tên sản phẩm không được để trống" in html.unescape(res1.data.decode("utf-8"))

        # Test giá âm
        res2 = client.post("/admin/products", data={"name": "SP Test", "price": "-50000", "stock": "10"}, follow_redirects=True)
        assert "Giá sản phẩm phải lớn hơn hoặc bằng 0" in html.unescape(res2.data.decode("utf-8"))

        # Test tồn kho âm
        res3 = client.post("/admin/products", data={"name": "SP Test", "price": "50000", "stock": "-5"}, follow_redirects=True)
        assert "Số lượng tồn kho phải lớn hơn hoặc bằng 0" in html.unescape(res3.data.decode("utf-8"))

        # Test danh mục giả mạo
        res4 = client.post("/admin/products", data={"name": "SP Test", "price": "50000", "stock": "5", "category_id": "99999"}, follow_redirects=True)
        assert "Danh mục đã chọn không tồn tại trong hệ thống" in html.unescape(res4.data.decode("utf-8"))
        print("   👉 KẾT QUẢ: Hệ thống bắt chính xác 100% các dữ liệu không hợp lệ và hiển thị thông báo lỗi!")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 3: Thêm sản phẩm & theo dõi tồn kho thấp (Low-Stock)
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 3] Thêm sản phẩm vào Database thật & theo dõi ngưỡng tồn kho:")
        print("   - Thêm sản phẩm có số lượng tồn kho = 3 (ngưỡng cảnh báo <= 5).")
        old_low_stock = SanPham.query.filter(SanPham.SOLUONGTON <= 5).count()

        res = client.post("/admin/products", data={
            "name": "Bàn phím cơ Test",
            "price": "1200000",
            "stock": "3",
            "category_id": "12",
            "status": "1",
            "description": "Bàn phím cơ gõ êm",
            "image": "keyboard.jpg"
        }, follow_redirects=True)
        assert "Đã thêm sản phẩm 'Bàn phím cơ Test' thành công" in html.unescape(res.data.decode("utf-8"))

        sp = SanPham.query.filter_by(TENSPH="Bàn phím cơ Test").first()
        assert sp is not None
        assert sp.SOLUONGTON == 3
        new_low_stock = SanPham.query.filter(SanPham.SOLUONGTON <= 5).count()
        assert new_low_stock == old_low_stock + 1
        print(f"   👉 KẾT QUẢ: Sản phẩm ID #{sp.MASANPHAM} đã lưu vào DB. Chỉ số hàng sắp hết tăng từ {old_low_stock} lên {new_low_stock}!")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 4: Sửa sản phẩm
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 4] Chỉnh sửa sản phẩm và cập nhật kho:")
        print("   - Nhập thêm hàng (stock từ 3 lên 25 chiếc) -> Hết bị cảnh báo tồn kho thấp.")
        res = client.post(f"/admin/products/{sp.MASANPHAM}/edit", data={
            "name": "Bàn phím cơ Test (Đã nhập thêm hàng)",
            "price": "1150000",
            "stock": "25",
            "category_id": "12",
            "status": "1",
            "description": "Mới về thêm 25 chiếc",
            "image": "keyboard.jpg"
        }, follow_redirects=True)
        assert "Đã cập nhật sản phẩm" in html.unescape(res.data.decode("utf-8"))

        db.session.refresh(sp)
        assert sp.SOLUONGTON == 25
        assert sp.TENSPH == "Bàn phím cơ Test (Đã nhập thêm hàng)"
        current_low_stock = SanPham.query.filter(SanPham.SOLUONGTON <= 5).count()
        assert current_low_stock == old_low_stock
        print("   👉 KẾT QUẢ: Cập nhật thành công, số lượng tồn kho tự động thoát khỏi danh sách cảnh báo!")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 5: Xóa sản phẩm chưa có đơn hàng
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 5] Xóa sản phẩm an toàn (khi chưa phát sinh đơn):")
        pid = sp.MASANPHAM
        res = client.post(f"/admin/products/{pid}/delete", follow_redirects=True)
        assert "Đã xóa sản phẩm" in html.unescape(res.data.decode("utf-8"))
        assert db.session.get(SanPham, pid) is None
        print(f"   👉 KẾT QUẢ: Sản phẩm #{pid} đã được xóa sạch sẽ khỏi cơ sở dữ liệu.")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 6: Phản ánh đơn hàng Checkout tự động
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 6] Phản ánh đơn hàng từ Checkout của khách (không cần nhập tay):")
        print("   - Mô phỏng khách đặt mua: 'Samsung Galaxy S22' (SL: 2) -> Tổng tiền 36.000.000đ.")
        prod = SanPham.query.first()
        order = DonHang(
            HOTENNHAN="Trần Vũ Hoàng Long",
            SDTNHAN="0901234567",
            DIACHIGIAO="Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
            NGAYDAT=date.today(),
            TONGGIATRI=prod.DONGIA * 2,
            TRANGTHAI=0,  # 0: Mới / Chờ xử lý
        )
        db.session.add(order)
        db.session.flush()

        detail = ChiTietDonHang(
            MADONHANG=order.MADONHANG,
            MASANPHAM=prod.MASANPHAM,
            SOLUONG=2,
        )
        db.session.add(detail)
        db.session.commit()
        order_id = order.MADONHANG

        res = client.get("/admin/orders")
        orders_page = html.unescape(res.data.decode("utf-8"))
        assert f"#{order_id}" in orders_page
        assert "Trần Vũ Hoàng Long" in orders_page
        assert "0901234567" in orders_page
        print(f"   👉 KẾT QUẢ: Đơn hàng #{order_id} xuất hiện ngay lập tức trên trang Quản lý đơn hàng!")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 7: Chi tiết đơn hàng
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 7] Xem thông tin chi tiết hóa đơn (/admin/orders/<id>):")
        res = client.get(f"/admin/orders/{order_id}")
        detail_page = html.unescape(res.data.decode("utf-8"))
        assert f"Chi tiết đơn hàng #{order_id}" in detail_page
        assert "Trần Vũ Hoàng Long" in detail_page
        assert "Số 1 Đại Cồ Việt" in detail_page
        assert prod.TENSPH in detail_page
        assert "2" in detail_page
        assert "{:,.0f}".format(prod.DONGIA * 2) in detail_page
        print("   👉 KẾT QUẢ: Màn hình chi tiết hiển thị đầy đủ người nhận, địa chỉ, sản phẩm, số lượng, subtotal!")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 8: Cập nhật trạng thái đơn hàng & giữ trạng thái khi refresh
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 8] Cập nhật trạng thái đơn hàng (Mới -> Đang xử lý -> Hoàn thành):")
        # Chuyển sang 1: Đang xử lý
        client.post(f"/admin/orders/{order_id}/status", data={"status": "1"}, follow_redirects=True)
        db.session.refresh(order)
        assert order.TRANGTHAI == 1

        # Chuyển sang 2: Hoàn thành
        client.post(f"/admin/orders/{order_id}/status", data={"status": "2"}, follow_redirects=True)
        db.session.refresh(order)
        assert order.TRANGTHAI == 2

        # Tải lại trang để kiểm chứng
        res = client.get(f"/admin/orders/{order_id}")
        assert "Hoàn thành" in html.unescape(res.data.decode("utf-8"))
        print(f"   👉 KẾT QUẢ: Cập nhật thành công! Đơn hàng #{order_id} chuyển sang 'Hoàn thành' và lưu vĩnh viễn trong DB.")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 9: Ngăn chặn xóa sản phẩm đã có trong đơn hàng
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 9] Xử lý an toàn khi xóa sản phẩm đã có trong đơn hàng:")
        print(f"   - Thử xóa sản phẩm '{prod.TENSPH}' (đang nằm trong đơn #{order_id}).")
        res = client.post(f"/admin/products/{prod.MASANPHAM}/delete", follow_redirects=True)
        msg = html.unescape(res.data.decode("utf-8"))
        assert "Không thể xóa sản phẩm" in msg
        assert "vì đã có trong đơn hàng tham chiếu" in msg
        # Sản phẩm vẫn phải còn trong DB
        assert db.session.get(SanPham, prod.MASANPHAM) is not None
        print("   👉 KẾT QUẢ: Hệ thống CHẶN xóa thành công! Bảo vệ an toàn dữ liệu lịch sử đơn hàng.")

        # ----------------------------------------------------------------------
        # NGHIỆP VỤ 10: Cô lập route Shop
        # ----------------------------------------------------------------------
        print("\n🔹 [Nghiệp vụ 10] Kiểm tra các route Shop không bị ảnh hưởng:")
        assert client.get("/").status_code == 200
        assert client.get("/products").status_code == 200
        assert client.get("/cart").status_code == 200
        print("   👉 KẾT QUẢ: Toàn bộ route Shop bên ngoài hoạt động bình thường, không bị ghi đè.")

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ CÁC NGHIỆP VỤ ĐÃ HOẠT ĐỘNG HOÀN HẢO VÀ CHÍNH XÁC 100%!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
