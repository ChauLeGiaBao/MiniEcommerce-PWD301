from app import create_app
from app.extensions import db
from app.models import DanhMuc, SanPham

CATEGORIES = [
    (11, "Điện thoại"),
    (12, "Laptop"),
    (21, "Thời trang nam"),
    (22, "Thời trang nữ"),
]

PRODUCTS = [
    ("Samsung Galaxy S22", "no-image.jpg", 18000000, "Samsung chính hãng, màn hình Dynamic AMOLED 6.1 inch", 15, 1, 11),
    ("iPhone 14", "no-image.jpg", 22000000, "Apple chính hãng, chip A15 Bionic, camera kép 12MP", 10, 1, 11),
    ("Xiaomi Redmi Note 12", "no-image.jpg", 5500000, "Pin 5000mAh, sạc nhanh 33W, giá tốt", 25, 1, 11),
    ("Oppo Reno 8", "no-image.jpg", 9500000, "Camera chân dung AI, thiết kế mỏng nhẹ", 18, 1, 11),
    ("Vivo V27", "no-image.jpg", 8200000, "Màn hình cong AMOLED, camera selfie 50MP", 12, 1, 11),
    ("MacBook Air M2", "no-image.jpg", 28000000, "Chip Apple M2, 8GB RAM, 256GB SSD", 8, 1, 12),
    ("Dell Inspiron 15", "no-image.jpg", 15500000, "Intel Core i5, 8GB RAM, phù hợp học tập văn phòng", 14, 1, 12),
    ("Asus Vivobook 14", "no-image.jpg", 13200000, "Thiết kế mỏng nhẹ, pin 10 tiếng", 20, 1, 12),
    ("Lenovo ThinkPad E14", "no-image.jpg", 17800000, "Bền bỉ, bảo mật cao, phù hợp doanh nghiệp", 9, 1, 12),
    ("HP Pavilion Gaming", "no-image.jpg", 21000000, "Card RTX 3050, phù hợp chơi game nhẹ và đồ họa", 6, 1, 12),
    ("Áo sơ mi nam trắng", "no-image.jpg", 350000, "Chất liệu cotton thoáng mát, form slim fit", 40, 1, 21),
    ("Quần jean nam xanh", "no-image.jpg", 480000, "Vải denim co giãn, form regular", 35, 1, 21),
    ("Áo thun nam basic", "no-image.jpg", 199000, "Cotton 100%, nhiều màu lựa chọn", 60, 1, 21),
    ("Áo khoác nam bomber", "no-image.jpg", 650000, "Giữ ấm tốt, phong cách năng động", 20, 1, 21),
    ("Quần short nam kaki", "no-image.jpg", 280000, "Thoải mái, phù hợp mùa hè", 30, 1, 21),
    ("Đầm nữ công sở", "no-image.jpg", 550000, "Thiết kế thanh lịch, phù hợp đi làm", 25, 1, 22),
    ("Áo kiểu nữ tay phồng", "no-image.jpg", 320000, "Chất liệu voan mềm mại, nữ tính", 30, 1, 22),
    ("Chân váy nữ xếp ly", "no-image.jpg", 380000, "Form A-line, dễ phối đồ", 28, 1, 22),
    ("Áo len nữ cổ lọ", "no-image.jpg", 420000, "Giữ ấm tốt, chất len mềm mịn", 22, 1, 22),
    ("Quần culottes nữ", "no-image.jpg", 350000, "Ống rộng thoải mái, phong cách trẻ trung", 18, 1, 22),
]

app = create_app()

with app.app_context():
    db.create_all()

    if DanhMuc.query.count() == 0:
        for category_id, name in CATEGORIES:
            db.session.add(DanhMuc(MADANHMUC=category_id, TENDM=name))

    if SanPham.query.count() == 0:
        for name, image, price, description, stock, status, category_id in PRODUCTS:
            db.session.add(
                SanPham(
                    TENSPH=name,
                    HINHANH=image,
                    DONGIA=price,
                    MOTA=description,
                    SOLUONGTON=stock,
                    TRANGTHAISPH=status,
                    MADANHMUC=category_id,
                )
            )

    db.session.commit()

    print("Database initialized successfully.")
    print("Categories:", DanhMuc.query.count())
    print("Products:", SanPham.query.count())
