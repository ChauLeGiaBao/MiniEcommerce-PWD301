"""
Khởi tạo database + dữ liệu mẫu cho MiniEcommerce-PWD301.

Cách chạy (đứng ở thư mục project, đã bật venv):
    python seed.py           -> tạo các bảng còn thiếu + thêm dữ liệu mẫu nếu bảng đang trống
    python seed.py --reset   -> XÓA toàn bộ bảng rồi tạo lại từ đầu (có hỏi xác nhận)

- Chạy nhiều lần không bị trùng dữ liệu.
- Dùng được cho SQL Server (khai báo DATABASE_URL trong file .env)
  và SQLite (mặc định khi không có DATABASE_URL).
- Bảng được tạo trực tiếp từ các model trong app/models, nên luôn khớp với code.
"""
import os
import sys

from dotenv import load_dotenv

# Phải nạp .env TRƯỚC khi import app, vì config.py đọc DATABASE_URL ngay lúc import
load_dotenv()

from flask_migrate import stamp            # noqa: E402
from sqlalchemy import inspect, text        # noqa: E402

from app import create_app                  # noqa: E402
from app.extensions import db               # noqa: E402
from app.models import DanhMuc, SanPham     # noqa: E402


MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")

DANH_MUC = [
    (11, "Điện thoại"),
    (12, "Laptop"),
    (21, "Thời trang nam"),
    (22, "Thời trang nữ"),
]

# (tên, đơn giá, mô tả, số lượng tồn, mã danh mục)
SAN_PHAM = [
    ("Samsung Galaxy S22", 18000000, "Samsung chính hãng, màn hình Dynamic AMOLED 6.1 inch", 15, 11),
    ("iPhone 14", 22000000, "Apple chính hãng, chip A15 Bionic, camera kép 12MP", 10, 11),
    ("Xiaomi Redmi Note 12", 5500000, "Pin 5000mAh, sạc nhanh 33W, giá tốt", 25, 11),
    ("Oppo Reno 8", 9500000, "Camera chân dung AI, thiết kế mỏng nhẹ", 18, 11),
    ("Vivo V27", 8200000, "Màn hình cong AMOLED, camera selfie 50MP", 12, 11),

    ("MacBook Air M2", 28000000, "Chip Apple M2, 8GB RAM, 256GB SSD", 8, 12),
    ("Dell Inspiron 15", 15500000, "Intel Core i5, 8GB RAM, phù hợp học tập văn phòng", 14, 12),
    ("Asus Vivobook 14", 13200000, "Thiết kế mỏng nhẹ, pin 10 tiếng", 20, 12),
    ("Lenovo ThinkPad E14", 17800000, "Bền bỉ, bảo mật cao, phù hợp doanh nghiệp", 9, 12),
    ("HP Pavilion Gaming", 21000000, "Card RTX 3050, phù hợp chơi game nhẹ và đồ họa", 6, 12),

    ("Áo sơ mi nam trắng", 350000, "Chất liệu cotton thoáng mát, form slim fit", 40, 21),
    ("Quần jean nam xanh", 480000, "Vải denim co giãn, form regular", 35, 21),
    ("Áo thun nam basic", 199000, "Cotton 100%, nhiều màu lựa chọn", 60, 21),
    ("Áo khoác nam bomber", 650000, "Giữ ấm tốt, phong cách năng động", 20, 21),
    ("Quần short nam kaki", 280000, "Thoải mái, phù hợp mùa hè", 30, 21),

    ("Đầm nữ công sở", 550000, "Thiết kế thanh lịch, phù hợp đi làm", 25, 22),
    ("Áo kiểu nữ tay phồng", 320000, "Chất liệu voan mềm mại, nữ tính", 30, 22),
    ("Chân váy nữ xếp ly", 380000, "Form A-line, dễ phối đồ", 28, 22),
    ("Áo len nữ cổ lọ", 420000, "Giữ ấm tốt, chất len mềm mịn", 22, 22),
    ("Quần culottes nữ", 350000, "Ống rộng thoải mái, phong cách trẻ trung", 18, 22),
]


def table_names():
    return {name.upper() for name in inspect(db.engine).get_table_names()}


def reset_database():
    answer = input("⚠ Lệnh này XÓA TOÀN BỘ bảng và dữ liệu. Gõ 'yes' để tiếp tục: ")
    if answer.strip().lower() != "yes":
        print("Đã hủy, không xóa gì.")
        sys.exit(0)

    db.drop_all()
    if "ALEMBIC_VERSION" in table_names():
        db.session.execute(text("DROP TABLE alembic_version"))
        db.session.commit()
    print("✔ Đã xóa toàn bộ bảng.")


def create_tables():
    before = table_names()
    db.create_all()

    # DB mới hoàn toàn: đánh dấu migration ở bản mới nhất,
    # để sau này `flask db upgrade` không chạy lại các bước đã có sẵn trong bảng.
    if "SANPHAM" not in before and "ALEMBIC_VERSION" not in before:
        stamp(directory=MIGRATIONS_DIR)
        print("✔ Đã tạo bảng mới và đánh dấu migration ở bản mới nhất.")
    else:
        print("✔ Bảng đã có sẵn, chỉ tạo thêm bảng còn thiếu (nếu có).")


def seed_categories():
    if DanhMuc.query.count() > 0:
        print("• DANHMUC đã có dữ liệu, bỏ qua.")
        return

    for ma, ten in DANH_MUC:
        db.session.add(DanhMuc(MADANHMUC=ma, TENDM=ten))
    db.session.commit()
    print(f"✔ Đã thêm {len(DANH_MUC)} danh mục.")


def seed_products():
    if SanPham.query.count() > 0:
        print("• SANPHAM đã có dữ liệu, bỏ qua.")
        return

    for ten, gia, mo_ta, ton, ma_dm in SAN_PHAM:
        db.session.add(SanPham(
            TENSPH=ten,
            HINHANH="no-image.jpg",
            DONGIA=gia,
            MOTA=mo_ta,
            SOLUONGTON=ton,
            TRANGTHAISPH=1,
            MADANHMUC=ma_dm,
        ))
    db.session.commit()
    print(f"✔ Đã thêm {len(SAN_PHAM)} sản phẩm.")


def main():
    app = create_app()

    with app.app_context():
        print("Database:", db.engine.url.render_as_string(hide_password=True))

        if "--reset" in sys.argv:
            reset_database()

        create_tables()
        seed_categories()
        seed_products()

        print(f"Xong! Hiện có {DanhMuc.query.count()} danh mục, {SanPham.query.count()} sản phẩm.")


if __name__ == "__main__":
    main()