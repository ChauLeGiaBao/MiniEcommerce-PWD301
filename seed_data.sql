-- ============================================
-- SCRIPT KHỞI TẠO DATABASE + SEED DATA
-- Dùng cho: MiniEcommerce-PWD301 (PWD301)
-- Chạy 1 lần trên database rỗng (EcommerceDB)
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
    DONGIA MONEY,
    MOTA NVARCHAR(500),
    SOLUONGTON INT DEFAULT 0,
    TRANGTHAISPH INT DEFAULT 1,
    MADANHMUC INT,
    CONSTRAINT FK_DMSPH FOREIGN KEY (MADANHMUC) REFERENCES DANHMUC(MADANHMUC)
);

CREATE TABLE NGUOIDUNG (
    MANGUOIDUNG INT IDENTITY PRIMARY KEY,
    HOTEN NVARCHAR(200) NOT NULL,
    EMAIL NVARCHAR(200),
    SDT CHAR(10),
    NGAYSINH DATE,
    PASSWORD_HASH NVARCHAR(255),
    ROLE NVARCHAR(20) DEFAULT 'customer',
    TRANGTHAIND INT DEFAULT 1
);

CREATE TABLE DONHANG (
    MADONHANG INT IDENTITY PRIMARY KEY,
    MANGUOIDUNG INT,
    NGAYDAT DATE,
    TONGGIATRI MONEY,
    TRANGTHAI INT DEFAULT 0,
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
(N'Samsung Galaxy S22', 'no-image.jpg', 18000000, N'Samsung chính hãng, màn hình Dynamic AMOLED 6.1 inch', 15, 1, 11),
(N'iPhone 14', 'no-image.jpg', 22000000, N'Apple chính hãng, chip A15 Bionic, camera kép 12MP', 10, 1, 11),
(N'Xiaomi Redmi Note 12', 'no-image.jpg', 5500000, N'Pin 5000mAh, sạc nhanh 33W, giá tốt', 25, 1, 11),
(N'Oppo Reno 8', 'no-image.jpg', 9500000, N'Camera chân dung AI, thiết kế mỏng nhẹ', 18, 1, 11),
(N'Vivo V27', 'no-image.jpg', 8200000, N'Màn hình cong AMOLED, camera selfie 50MP', 12, 1, 11),

(N'MacBook Air M2', 'no-image.jpg', 28000000, N'Chip Apple M2, 8GB RAM, 256GB SSD', 8, 1, 12),
(N'Dell Inspiron 15', 'no-image.jpg', 15500000, N'Intel Core i5, 8GB RAM, phù hợp học tập văn phòng', 14, 1, 12),
(N'Asus Vivobook 14', 'no-image.jpg', 13200000, N'Thiết kế mỏng nhẹ, pin 10 tiếng', 20, 1, 12),
(N'Lenovo ThinkPad E14', 'no-image.jpg', 17800000, N'Bền bỉ, bảo mật cao, phù hợp doanh nghiệp', 9, 1, 12),
(N'HP Pavilion Gaming', 'no-image.jpg', 21000000, N'Card RTX 3050, phù hợp chơi game nhẹ và đồ họa', 6, 1, 12),

(N'Áo sơ mi nam trắng', 'no-image.jpg', 350000, N'Chất liệu cotton thoáng mát, form slim fit', 40, 1, 21),
(N'Quần jean nam xanh', 'no-image.jpg', 480000, N'Vải denim co giãn, form regular', 35, 1, 21),
(N'Áo thun nam basic', 'no-image.jpg', 199000, N'Cotton 100%, nhiều màu lựa chọn', 60, 1, 21),
(N'Áo khoác nam bomber', 'no-image.jpg', 650000, N'Giữ ấm tốt, phong cách năng động', 20, 1, 21),
(N'Quần short nam kaki', 'no-image.jpg', 280000, N'Thoải mái, phù hợp mùa hè', 30, 1, 21),

(N'Đầm nữ công sở', 'no-image.jpg', 550000, N'Thiết kế thanh lịch, phù hợp đi làm', 25, 1, 22),
(N'Áo kiểu nữ tay phồng', 'no-image.jpg', 320000, N'Chất liệu voan mềm mại, nữ tính', 30, 1, 22),
(N'Chân váy nữ xếp ly', 'no-image.jpg', 380000, N'Form A-line, dễ phối đồ', 28, 1, 22),
(N'Áo len nữ cổ lọ', 'no-image.jpg', 420000, N'Giữ ấm tốt, chất len mềm mịn', 22, 1, 22),
(N'Quần culottes nữ', 'no-image.jpg', 350000, N'Ống rộng thoải mái, phong cách trẻ trung', 18, 1, 22);