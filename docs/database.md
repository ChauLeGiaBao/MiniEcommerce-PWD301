# Tài liệu database – Mini E-Commerce Store (PWD301)

Database: **SQL Server** (`MiniEcommerceDB`), truy cập bằng Flask-SQLAlchemy.
Schema do các model trong `app/models/` quyết định, thay đổi schema thông qua Flask-Migrate (thư mục `migrations/`).

## 1. Sơ đồ quan hệ

```mermaid
erDiagram
    DANHMUC ||--o{ SANPHAM : "có"
    NGUOIDUNG |o--o{ DONHANG : "đặt"
    DONHANG ||--|{ CHITIETDONHANG : "gồm"
    SANPHAM ||--o{ CHITIETDONHANG : "xuất hiện trong"
    NGUOIDUNG ||--o{ DANHGIA : "viết"
    SANPHAM ||--o{ DANHGIA : "nhận"
```

- Danh mục **phẳng một cấp** (đã bỏ cột `MADMCHA`).
- `DONHANG.MANGUOIDUNG` có thể là `NULL`: khách chưa đăng nhập vẫn đặt hàng được.
- `DANHGIA` là quan hệ nhiều-nhiều (M:N) giữa `NGUOIDUNG` và `SANPHAM` kèm ràng buộc một user chỉ đánh giá một sản phẩm một lần.

## 2. Các bảng

### DANHMUC (model `DanhMuc`)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| MADANHMUC | INT, PK | Nhập tay, không tự tăng |
| TENDM | NVARCHAR(50) | Tên danh mục |

### SANPHAM (model `SanPham`)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| MASANPHAM | INT, PK, tự tăng | |
| TENSPH | NVARCHAR(200) | Tên sản phẩm |
| HINHANH | VARCHAR(500) | Link ảnh `http(s)://...`. Rỗng hoặc không phải link (vd `no-image.jpg`) thì web hiện ảnh mặc định |
| DONGIA | NUMERIC(18,2) | Đơn giá (đ) |
| MOTA | NVARCHAR(500) | Mô tả |
| SOLUONGTON | INT, mặc định 0 | Tồn kho; có CHECK constraint `CK_SANPHAM_SOLUONGTON` (`SOLUONGTON >= 0`) |
| TRANGTHAISPH | INT, mặc định 1 | `1` = Đang bán (Active), `0` = Tạm ẩn (Inactive) |
| MADANHMUC | INT, FK → DANHMUC | |

### NGUOIDUNG (model `User`)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| MANGUOIDUNG | INT, PK, tự tăng | |
| HOTEN | NVARCHAR(200), NOT NULL | |
| EMAIL | VARCHAR(200) | Địa chỉ email đăng nhập (kiểm tra unique ở tầng service/form) |
| SDT | VARCHAR(10) | |
| NGAYSINH | DATE | |
| PASSWORD_HASH | VARCHAR(255) | Mật khẩu đã băm bằng Werkzeug (PBKDF2/scrypt), không lưu mật khẩu thô |
| ROLE | VARCHAR(20), mặc định `customer` | Vai trò: `customer`, `staff`, `admin` |
| TRANGTHAIND | INT, mặc định 1 | Trạng thái tài khoản (1 = Hoạt động, 0 = Bị khóa) |

### DONHANG (model `DonHang`)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| MADONHANG | INT, PK, tự tăng | |
| MANGUOIDUNG | INT, FK → NGUOIDUNG, NULL | NULL nếu khách chưa đăng nhập |
| NGAYDAT | DATE | |
| TONGGIATRI | NUMERIC(18,2) | Tổng tiền, lưu lúc đặt hàng |
| TRANGTHAI | INT, mặc định 0 | `0` Mới / chờ xử lý, `1` Đang xử lý, `2` Hoàn thành, `3` Đã hủy |
| HOTENNHAN | NVARCHAR(200) | Người nhận (từ form checkout) |
| DIACHIGIAO | NVARCHAR(300) | Địa chỉ giao hàng |
| SDTNHAN | VARCHAR(15) | Số điện thoại nhận hàng |

### CHITIETDONHANG (model `ChiTietDonHang`)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| MADONHANG | INT, PK, FK → DONHANG | |
| MASANPHAM | INT, PK, FK → SANPHAM | |
| SOLUONG | INT | |

Khóa chính ghép `(MADONHANG, MASANPHAM)`: một sản phẩm chỉ xuất hiện một lần trong một đơn.

### Quan hệ trong code
- `DanhMuc.sanpham_list` ↔ `SanPham.danhmuc`
- `User.donhang_list` ↔ `DonHang.user`
- `DonHang.chitiet_list` ↔ `ChiTietDonHang.donhang`
- `ChiTietDonHang.sanpham`

## 3. Quy tắc nghiệp vụ

- **Chỉ sản phẩm Active (`TRANGTHAISPH = 1`)** hiện ở trang shop. Trang chi tiết của sản phẩm Inactive trả 404. Trang admin vẫn thấy tất cả.
- **Giá và tồn kho không âm:** được kiểm tra khi thêm/sửa sản phẩm trong admin (chưa có CHECK constraint ở database).
- **Hết hàng** (`SOLUONGTON = 0`): hiện nhãn "Hết hàng", không cho thêm vào giỏ. Khi đặt hàng, hệ thống kiểm tra lại tồn kho và trừ kho.
- **Sort "Mới nhất"** = `MASANPHAM` lớn nhất trước (chưa có cột ngày tạo).
- **Tìm kiếm** theo tên và mô tả, không phân biệt hoa thường; ký tự `%`, `_`, `[` được tìm theo nghĩa đen.
- **Lọc giá** `min_price` / `max_price`: giá không hợp lệ bị bỏ qua kèm cảnh báo; nếu min lớn hơn max thì hai giá trị tự đổi chỗ.
- Logic truy vấn sản phẩm nằm trong `app/services/product_service.py` (`get_products`, `get_product_by_id`, `get_categories`, `is_available`). Route và API nên gọi các hàm này thay vì tự viết query.

## 4. Cài đặt database

### 4.1. Cấu hình kết nối
Tạo file `.env` ở thư mục gốc (file này không được commit), ví dụ với SQL Server Express dùng Windows Authentication:

```
DATABASE_URL=mssql+pyodbc://@localhost\SQLEXPRESS/EcommerceDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

Sửa tên máy, tên instance, tên driver cho đúng máy của bạn. Nếu không có `DATABASE_URL`, ứng dụng dùng SQLite `dev.db` (chỉ để thử).
Tạo sẵn database trống `EcommerceDB` trong SSMS trước.

### 4.2. Database mới (khuyên dùng)
```
python seed.py
```
Lệnh này tạo các bảng từ model, đánh dấu migration ở bản mới nhất và thêm dữ liệu mẫu (4 danh mục, 20 sản phẩm). Chạy lại nhiều lần không bị trùng dữ liệu.
Muốn xóa sạch và làm lại từ đầu: `python seed.py --reset` (có hỏi xác nhận).

### 4.3. Database đã có sẵn từ các tuần trước
```
flask db upgrade
flask db check
```
`flask db check` phải báo `No new upgrade operations detected`.

### 4.4. Cách khác: chạy script SQL
Chạy `seed_data.sql` trong SSMS trên database trống, sau đó chạy `flask db stamp head` (nếu thiếu bước này, `flask db upgrade` sẽ báo lỗi bảng đã tồn tại).

## 5. Migration

Lịch sử migration (`migrations/versions/`):

| Revision | Nội dung |
|---|---|
| `f14dcd86bf53` | Nới `SANPHAM.HINHANH` lên 500 ký tự |
| `b2a434abe7a9` | Thêm `HOTENNHAN`, `DIACHIGIAO`, `SDTNHAN` vào `DONHANG` |
| `c562dfbd1758` | Đổi `DONHANG.TONGGIATRI` sang NUMERIC(18,2), `NGUOIDUNG.SDT` sang VARCHAR(10) |

Khi đổi model:
```
flask db migrate -m "mô tả ngắn"
```
Mở file mới trong `migrations/versions/` để kiểm tra (không được có `drop_table` ngoài ý muốn), sau đó:
```
flask db upgrade
flask db check
```
Hai bảng `DANHMUC_BACKUP` và `SANPHAM_BACKUP` (bản sao lưu cũ, không thuộc model) đã được bỏ qua trong `migrations/env.py`, nên Alembic không đề xuất xóa chúng.

## 6. Lưu ý với SQL Server

- Phân trang bắt buộc có `ORDER BY`, và **một cột không được xuất hiện hai lần** trong `ORDER BY`.
- Cột tiếng Việt dùng `Unicode` (NVARCHAR) trong model để lưu có dấu.
- Dùng `Numeric(18,2)` thay cho `MONEY` để model và database khớp nhau.

## 7. Hạn chế đã biết

- `CHITIETDONHANG` không lưu đơn giá tại thời điểm mua, nên đổi giá sản phẩm sẽ làm thành tiền từng dòng trong đơn cũ hiển thị theo giá mới (`TONGGIATRI` của đơn vẫn giữ nguyên giá lúc đặt).
- Chưa có cột ngày tạo cho sản phẩm.
- Đã có CHECK constraint `CK_SANPHAM_SOLUONGTON` (`SOLUONGTON >= 0`) ở database (migration `4877af4546c5`); kiểm tra đơn giá không âm nằm ở tầng validation logic/form admin.

## Bảng DANHGIA (đánh giá sản phẩm, quan hệ M:N User - Product)

Bảng liên kết thật sự giữa `NGUOIDUNG` và `SANPHAM`: một user đánh giá nhiều sản phẩm,
một sản phẩm được nhiều user đánh giá.

| Cột | Kiểu | Ràng buộc |
|---|---|---|
| MADANHGIA | INT | PK, tự tăng |
| MANGUOIDUNG | INT | NOT NULL, FK -> NGUOIDUNG.MANGUOIDUNG |
| MASANPHAM | INT | NOT NULL, FK -> SANPHAM.MASANPHAM |
| SOSAO | INT | NOT NULL, CHECK (SOSAO BETWEEN 1 AND 5) |
| NOIDUNG | NVARCHAR(1000) | NULL |
| NGAYTAO | DATETIME | NOT NULL |

- `UNIQUE (MANGUOIDUNG, MASANPHAM)` (tên `UQ_DANHGIA_USER_SP`): mỗi user chỉ đánh giá 1 lần cho mỗi sản phẩm.
- `CHECK` tên `CK_DANHGIA_SOSAO`: chặn điểm ngoài khoảng 1-5.
- Migration: `b9953ac12c5e_add_danhgia_review_table.py` (sau `c562dfbd1758`).
- Policy hiện tại: chưa yêu cầu đã mua hàng mới được đánh giá (chờ nhóm xác nhận).

```mermaid
erDiagram
    NGUOIDUNG ||--o{ DANHGIA : "viet"
    SANPHAM ||--o{ DANHGIA : "co"
    NGUOIDUNG {
        int MANGUOIDUNG PK
    }
    SANPHAM {
        int MASANPHAM PK
    }
    DANHGIA {
        int MADANHGIA PK
        int MANGUOIDUNG FK
        int MASANPHAM FK
        int SOSAO
        string NOIDUNG
        datetime NGAYTAO
    }
```
## Ràng buộc tồn kho và dữ liệu demo

- `SANPHAM`: `CHECK (SOLUONGTON >= 0)` (tên `CK_SANPHAM_SOLUONGTON`), không cho tồn kho âm.
- Migration: `4877af4546c5_add_stock_non_negative_check.py` (sau `b9953ac12c5e`).
- `seed.py` có thêm 3 sản phẩm demo: hết hàng (tồn 0), sắp hết hàng (tồn 3), tạm ẩn (TRANGTHAISPH = 0). Chạy lặp không bị trùng (kiểm tra theo tên sản phẩm).
- Chuỗi migration hiện tại: `f14dcd86bf53` → `b2a434abe7a9` → `c562dfbd1758` → `b9953ac12c5e` → `4877af4546c5`.
- Không dùng `python seed.py --reset` trên DB đang có dữ liệu thật.
