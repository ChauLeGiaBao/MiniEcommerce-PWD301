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

# (tên, đơn giá, mô tả, số lượng tồn, mã danh mục, hình ảnh)
SAN_PHAM = [
    ("Samsung Galaxy S22", 18000000, "Samsung chính hãng, màn hình Dynamic AMOLED 6.1 inch", 15, 11, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=800&q=80"),
    ("iPhone 14", 22000000, "Apple chính hãng, chip A15 Bionic, camera kép 12MP", 10, 11, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80"),
    ("Xiaomi Redmi Note 12", 5500000, "Pin 5000mAh, sạc nhanh 33W, giá tốt", 25, 11, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80"),
    ("Oppo Reno 8", 9500000, "Camera chân dung AI, thiết kế mỏng nhẹ", 18, 11, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80"),
    ("Vivo V27", 8200000, "Màn hình cong AMOLED, camera selfie 50MP", 12, 11, "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=800&q=80"),

    ("MacBook Air M2", 28000000, "Chip Apple M2, 8GB RAM, 256GB SSD", 8, 12, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80"),
    ("Dell Inspiron 15", 15500000, "Intel Core i5, 8GB RAM, phù hợp học tập văn phòng", 14, 12, "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80"),
    ("Asus Vivobook 14", 13200000, "Thiết kế mỏng nhẹ, pin 10 tiếng", 20, 12, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80"),
    ("Lenovo ThinkPad E14", 17800000, "Bền bỉ, bảo mật cao, phù hợp doanh nghiệp", 9, 12, "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80"),
    ("HP Pavilion Gaming", 21000000, "Card RTX 3050, phù hợp chơi game nhẹ và đồ họa", 6, 12, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80"),

    ("Áo sơ mi nam trắng", 350000, "Chất liệu cotton thoáng mát, form slim fit", 40, 21, "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80"),
    ("Quần jean nam xanh", 480000, "Vải denim co giãn, form regular", 35, 21, "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80"),
    ("Áo thun nam basic", 199000, "Cotton 100%, nhiều màu lựa chọn", 60, 21, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80"),
    ("Áo khoác nam bomber", 650000, "Giữ ấm tốt, phong cách năng động", 20, 21, "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80"),
    ("Quần short nam kaki", 280000, "Thoải mái, phù hợp mùa hè", 30, 21, "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=800&q=80"),

    ("Đầm nữ công sở", 550000, "Thiết kế thanh lịch, phù hợp đi làm", 25, 22, "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=800&q=80"),
    ("Áo kiểu nữ tay phồng", 320000, "Chất liệu voan mềm mại, nữ tính", 30, 22, "https://images.unsplash.com/photo-1564257631407-4deb1f99d992?auto=format&fit=crop&w=800&q=80"),
    ("Chân váy nữ xếp ly", 380000, "Form A-line, dễ phối đồ", 28, 22, "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=800&q=80"),
    ("Áo len nữ cổ lọ", 420000, "Giữ ấm tốt, chất len mềm mịn", 22, 22, "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=800&q=80"),
    ("Quần culottes nữ", 350000, "Ống rộng thoải mái, phong cách trẻ trung", 18, 22, "https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?auto=format&fit=crop&w=800&q=80"),
]

# (tên, đơn giá, mô tả, số lượng tồn, mã danh mục, trạng thái: 1 đang bán / 0 tạm ẩn, hình ảnh)
SAN_PHAM_DEMO = [
    ("Tai nghe Bluetooth X1", 450000, "Demo sản phẩm hết hàng", 0, 11, 1, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80"),
    ("Sạc nhanh 20W", 290000, "Demo sản phẩm sắp hết hàng", 3, 11, 1, "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80"),
    ("Ốp lưng iPhone 14", 120000, "Demo sản phẩm tạm ẩn", 20, 11, 0, "https://images.unsplash.com/photo-1601593346740-925612772716?auto=format&fit=crop&w=800&q=80"),
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

    for item in SAN_PHAM:
        ten, gia, mo_ta, ton, ma_dm = item[:5]
        hinh_anh = item[5] if len(item) > 5 else "no-image.jpg"
        db.session.add(SanPham(
            TENSPH=ten,
            HINHANH=hinh_anh,
            DONGIA=gia,
            MOTA=mo_ta,
            SOLUONGTON=ton,
            TRANGTHAISPH=1,
            MADANHMUC=ma_dm,
        ))
    db.session.commit()
    print(f"✔ Đã thêm {len(SAN_PHAM)} sản phẩm.")

def seed_demo_products():
    """Thêm sản phẩm demo (hết hàng, sắp hết, tạm ẩn). Chạy lặp không bị trùng."""
    added = 0
    for item in SAN_PHAM_DEMO:
        ten, gia, mo_ta, ton, ma_dm, trang_thai = item[:6]
        hinh_anh = item[6] if len(item) > 6 else "no-image.jpg"
        if SanPham.query.filter_by(TENSPH=ten).first():
            continue
        db.session.add(SanPham(
            TENSPH=ten,
            HINHANH=hinh_anh,
            DONGIA=gia,
            MOTA=mo_ta,
            SOLUONGTON=ton,
            TRANGTHAISPH=trang_thai,
            MADANHMUC=ma_dm,
        ))
        added += 1
    db.session.commit()
    if added:
        print(f"✔ Đã thêm {added} sản phẩm demo.")
    else:
        print("• Sản phẩm demo đã có, bỏ qua.")

def main():
    app = create_app()

    with app.app_context():
        print("Database:", db.engine.url.render_as_string(hide_password=True))

        if "--reset" in sys.argv:
            reset_database()

        create_tables()
        seed_categories()
        seed_products()
        seed_demo_products()

        print(f"Xong! Hiện có {DanhMuc.query.count()} danh mục, {SanPham.query.count()} sản phẩm.")


if __name__ == "__main__":
    main()