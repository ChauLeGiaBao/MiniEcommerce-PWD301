"""Cấu hình pytest: dùng SQLite trong bộ nhớ, KHÔNG đụng tới SQL Server thật.

Phải gán DATABASE_URL TRƯỚC khi import app, vì config.py đọc biến này ngay lúc import.
Chạy test:  pytest        (từ thư mục gốc của project, đã bật venv)
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"  # SQLite in-memory

import pytest  # noqa: E402

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import DanhMuc, SanPham  # noqa: E402


def seed_sample_data():
    """Dữ liệu mẫu nhỏ, cố định để test biết chính xác kết quả mong đợi.

    Sản phẩm (ID tăng dần theo thứ tự thêm):
      1 Alpha Phone   22.000.000  tồn 10  danh mục 11  ảnh: link https
      2 Beta Phone    18.000.000  tồn 5   danh mục 11  ảnh: no-image.jpg
      3 Gamma Laptop  28.000.000  tồn 3   danh mục 12  ảnh: None
      4 Delta Phone    5.000.000  tồn 0   danh mục 11  (hết hàng)
      5 Hidden Phone   7.000.000  tồn 9   danh mục 11  (Inactive, không hiện ở shop)
    Danh mục 13 "Empty" không có sản phẩm nào.
    """
    db.session.add_all([
        DanhMuc(MADANHMUC=11, TENDM="Phone"),
        DanhMuc(MADANHMUC=12, TENDM="Laptop"),
        DanhMuc(MADANHMUC=13, TENDM="Empty"),
    ])
    db.session.add_all([
        SanPham(TENSPH="Alpha Phone", HINHANH="https://example.com/alpha.jpg", DONGIA=22000000,
                MOTA="Apple chip", SOLUONGTON=10, TRANGTHAISPH=1, MADANHMUC=11),
        SanPham(TENSPH="Beta Phone", HINHANH="no-image.jpg", DONGIA=18000000,
                MOTA="Màn hình AMOLED", SOLUONGTON=5, TRANGTHAISPH=1, MADANHMUC=11),
        SanPham(TENSPH="Gamma Laptop", HINHANH=None, DONGIA=28000000,
                MOTA="Chip M2", SOLUONGTON=3, TRANGTHAISPH=1, MADANHMUC=12),
        SanPham(TENSPH="Delta Phone", HINHANH="no-image.jpg", DONGIA=5000000,
                MOTA="Giá rẻ", SOLUONGTON=0, TRANGTHAISPH=1, MADANHMUC=11),
        SanPham(TENSPH="Hidden Phone", HINHANH="no-image.jpg", DONGIA=7000000,
                MOTA="Đang ẩn", SOLUONGTON=9, TRANGTHAISPH=0, MADANHMUC=11),
    ])
    db.session.commit()


@pytest.fixture()
def app():
    flask_app = create_app()
    flask_app.config.update(TESTING=True)

    with flask_app.app_context():
        # Chốt an toàn: tuyệt đối không create_all/drop_all trên DB thật
        if not str(db.engine.url).startswith("sqlite"):
            pytest.exit("Test phải chạy trên SQLite, không phải DB thật. Kiểm tra DATABASE_URL.")

        db.create_all()
        seed_sample_data()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()