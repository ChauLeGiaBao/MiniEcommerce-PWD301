from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import ChiTietDonHang, DanhMuc, DonHang, SanPham, User


def test_category_and_product_relationship(app):
    phone = db.session.get(DanhMuc, 11)
    names = sorted(p.TENSPH for p in phone.sanpham_list)

    # Danh mục 11 có 4 sản phẩm trong dữ liệu mẫu (kể cả Inactive, vì đây là quan hệ thô)
    assert names == ["Alpha Phone", "Beta Phone", "Delta Phone", "Hidden Phone"]

    alpha = db.session.get(SanPham, 1)
    assert alpha.danhmuc.TENDM == "Phone"


def test_category_is_flat(app):
    # Đã bỏ cấu trúc cha/con: model không còn cột MADMCHA
    assert not hasattr(DanhMuc, "MADMCHA")


def test_product_defaults(app):
    product = SanPham(TENSPH="Mặc định", DONGIA=1000)
    db.session.add(product)
    db.session.commit()

    assert product.SOLUONGTON == 0
    assert product.TRANGTHAISPH == 1  # 1 = Active


def test_user_default_role(app):
    user = User(HOTEN="Nguyen Van A", EMAIL="a@example.com")
    db.session.add(user)
    db.session.commit()

    assert user.ROLE == "customer"
    assert user.TRANGTHAIND == 1


def test_order_relationships_with_user(app):
    user = User(HOTEN="Nguyen Van A")
    db.session.add(user)
    db.session.flush()

    order = DonHang(MANGUOIDUNG=user.MANGUOIDUNG, NGAYDAT=date.today(), TONGGIATRI=44000000,
                    HOTENNHAN="Nguyen Van A", DIACHIGIAO="Ha Noi", SDTNHAN="0901234567")
    db.session.add(order)
    db.session.flush()
    db.session.add(ChiTietDonHang(MADONHANG=order.MADONHANG, MASANPHAM=1, SOLUONG=2))
    db.session.commit()

    assert order.TRANGTHAI == 0  # 0 = Mới / chờ xử lý
    assert order.user.HOTEN == "Nguyen Van A"
    assert user.donhang_list[0].MADONHANG == order.MADONHANG
    assert order.chitiet_list[0].SOLUONG == 2
    assert order.chitiet_list[0].sanpham.TENSPH == "Alpha Phone"


def test_guest_order_has_no_user(app):
    # Khách chưa đăng nhập: MANGUOIDUNG = NULL vẫn hợp lệ
    order = DonHang(MANGUOIDUNG=None, NGAYDAT=date.today(), TONGGIATRI=1000, HOTENNHAN="Khach")
    db.session.add(order)
    db.session.commit()

    assert order.user is None


def test_order_detail_primary_key_is_unique(app):
    order = DonHang(NGAYDAT=date.today(), TONGGIATRI=1000)
    db.session.add(order)
    db.session.flush()

    db.session.add(ChiTietDonHang(MADONHANG=order.MADONHANG, MASANPHAM=1, SOLUONG=1))
    db.session.commit()

    # Cùng (đơn hàng, sản phẩm) không được xuất hiện 2 lần
    db.session.add(ChiTietDonHang(MADONHANG=order.MADONHANG, MASANPHAM=1, SOLUONG=3))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()