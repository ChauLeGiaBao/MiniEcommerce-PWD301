-- ============================================
-- SCRIPT KHỞI TẠO DATABASE + SEED DATA
-- Dùng cho: MiniEcommerce-PWD301 (PWD301)
-- Chạy 1 lần trên database rỗng (EcommerceDB)
--
-- Sau khi chạy script này, mở terminal ở thư mục project và chạy:
--     flask db stamp head
-- (để Flask-Migrate biết DB đã ở phiên bản mới nhất,
--  nếu không flask db upgrade sẽ báo lỗi "table already exists")
--
-- Cách đơn giản hơn: bỏ qua file này và chạy  python seed.py
-- ============================================

-- ==== TẠO BẢNG ====

CREATE TABLE DANHMUC (
    MADANHMUC INT NOT NULL PRIMARY KEY,
    TENDM NVARCHAR(50)
);

CREATE TABLE SANPHAM (
    MASANPHAM INT IDENTITY PRIMARY KEY,
    TENSPH NVARCHAR(200),
    HINHANH VARCHAR(500),
    DONGIA DECIMAL(18,2),
    MOTA NVARCHAR(500),
    SOLUONGTON INT DEFAULT 0,
    TRANGTHAISPH INT DEFAULT 1,   -- 1 = Đang bán (Active), 0 = Tạm ẩn (Inactive)
    MADANHMUC INT,
    CONSTRAINT FK_DMSPH FOREIGN KEY (MADANHMUC) REFERENCES DANHMUC(MADANHMUC)
);

CREATE TABLE NGUOIDUNG (
    MANGUOIDUNG INT IDENTITY PRIMARY KEY,
    HOTEN NVARCHAR(200) NOT NULL,
    EMAIL NVARCHAR(200),
    SDT VARCHAR(10),
    NGAYSINH DATE,
    PASSWORD_HASH NVARCHAR(255),
    ROLE NVARCHAR(20) DEFAULT 'customer',
    TRANGTHAIND INT DEFAULT 1
);

CREATE TABLE DONHANG (
    MADONHANG INT IDENTITY PRIMARY KEY,
    MANGUOIDUNG INT,              -- NULL nếu khách đặt hàng khi chưa đăng nhập
    NGAYDAT DATE,
    TONGGIATRI DECIMAL(18,2),
    TRANGTHAI INT DEFAULT 0,      -- 0 Mới, 1 Đang xử lý, 2 Hoàn thành, 3 Đã hủy
    HOTENNHAN NVARCHAR(200),
    DIACHIGIAO NVARCHAR(300),
    SDTNHAN VARCHAR(15),
    CONSTRAINT FK_DH_USER FOREIGN KEY (MANGUOIDUNG) REFERENCES NGUOIDUNG(MANGUOIDUNG)
);

CREATE TABLE CHITIETDONHANG (
    MADONHANG INT NOT NULL,
    MASANPHAM INT NOT NULL,
    SOLUONG INT,
    CONSTRAINT PK_CTDH PRIMARY KEY (MADONHANG, MASANPHAM),
    CONSTRAINT FK_CTDH_DH FOREIGN KEY (MADONHANG) REFERENCES DONHANG(MADONHANG),
    CONSTRAINT FK_CTDH_SP FOREIGN KEY (MASANPHAM) REFERENCES SANPHAM(MASANPHAM)
);

-- ==== DANH MỤC (4 danh mục phẳng) ====

INSERT INTO DANHMUC (MADANHMUC, TENDM) VALUES
(11, N'Điện thoại'),
(12, N'Laptop'),
(21, N'Thời trang nam'),
(22, N'Thời trang nữ');

-- ==== SẢN PHẨM (20 sản phẩm, 5 sản phẩm/danh mục) ====

INSERT INTO SANPHAM (TENSPH, HINHANH, DONGIA, MOTA, SOLUONGTON, TRANGTHAISPH, MADANHMUC) VALUES
(N'Samsung Galaxy S22', 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=800&q=80', 18000000, N'Samsung chính hãng, màn hình Dynamic AMOLED 6.1 inch', 15, 1, 11),
(N'iPhone 14', 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80', 22000000, N'Apple chính hãng, chip A15 Bionic, camera kép 12MP', 10, 1, 11),
(N'Xiaomi Redmi Note 12', 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80', 5500000, N'Pin 5000mAh, sạc nhanh 33W, giá tốt', 25, 1, 11),
(N'Oppo Reno 8', 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80', 9500000, N'Camera chân dung AI, thiết kế mỏng nhẹ', 18, 1, 11),
(N'Vivo V27', 'https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=800&q=80', 8200000, N'Màn hình cong AMOLED, camera selfie 50MP', 12, 1, 11),

(N'MacBook Air M2', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80', 28000000, N'Chip Apple M2, 8GB RAM, 256GB SSD', 8, 1, 12),
(N'Dell Inspiron 15', 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80', 15500000, N'Intel Core i5, 8GB RAM, phù hợp học tập văn phòng', 14, 1, 12),
(N'Asus Vivobook 14', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80', 13200000, N'Thiết kế mỏng nhẹ, pin 10 tiếng', 20, 1, 12),
(N'Lenovo ThinkPad E14', 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80', 17800000, N'Bền bỉ, bảo mật cao, phù hợp doanh nghiệp', 9, 1, 12),
(N'HP Pavilion Gaming', 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80', 21000000, N'Card RTX 3050, phù hợp chơi game nhẹ và đồ họa', 6, 1, 12),

(N'Áo sơ mi nam trắng', 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80', 350000, N'Chất liệu cotton thoáng mát, form slim fit', 40, 1, 21),
(N'Quần jean nam xanh', 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80', 480000, N'Vải denim co giãn, form regular', 35, 1, 21),
(N'Áo thun nam basic', 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80', 199000, N'Cotton 100%, nhiều màu lựa chọn', 60, 1, 21),
(N'Áo khoác nam bomber', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80', 650000, N'Giữ ấm tốt, phong cách năng động', 20, 1, 21),
(N'Quần short nam kaki', 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=800&q=80', 280000, N'Thoải mái, phù hợp mùa hè', 30, 1, 21),

(N'Đầm nữ công sở', 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=800&q=80', 550000, N'Thiết kế thanh lịch, phù hợp đi làm', 25, 1, 22),
(N'Áo kiểu nữ tay phồng', 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?auto=format&fit=crop&w=800&q=80', 320000, N'Chất liệu voan mềm mại, nữ tính', 30, 1, 22),
(N'Chân váy nữ xếp ly', 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=800&q=80', 380000, N'Form A-line, dễ phối đồ', 28, 1, 22),
(N'Áo len nữ cổ lọ', 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=800&q=80', 420000, N'Giữ ấm tốt, chất len mềm mịn', 22, 1, 22),
(N'Quần culottes nữ', 'https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?auto=format&fit=crop&w=800&q=80', 350000, N'Ống rộng thoải mái, phong cách trẻ trung', 18, 1, 22);