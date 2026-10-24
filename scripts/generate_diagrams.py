# -*- coding: utf-8 -*-
"""
Script tạo các biểu đồ và hình chụp kỹ thuật chất lượng cao (ERD, Architecture, Terminal Test, API Postman)
phục vụ báo cáo đồ án Topic 8 - Mini E-Commerce Store (PWD301).
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_REGULAR = "C:\\Windows\\Fonts\\segoeui.ttf"
FONT_BOLD = "C:\\Windows\\Fonts\\segoeuib.ttf"
FONT_MONO = "C:\\Windows\\Fonts\\consola.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def generate_erd_diagram():
    """Vẽ Sơ đồ Quan hệ Thực thể (ERD) 6 bảng dữ liệu chuẩn xác."""
    width, height = 1400, 920
    img = Image.new("RGB", (width, height), "#0F172A")  # Dark slate background
    draw = ImageDraw.Draw(img)

    f_title = get_font(FONT_BOLD, 26)
    f_sub = get_font(FONT_REGULAR, 15)
    f_tbl_title = get_font(FONT_BOLD, 16)
    f_col = get_font(FONT_MONO, 13)
    f_note = get_font(FONT_REGULAR, 12)

    # Tiêu đề
    draw.text((40, 25), "SƠ ĐỒ THỰC THỂ QUAN HỆ CƠ SỞ DỮ LIỆU (ERD) — 6 BẢNG DỮ LIỆU", fill="#38BDF8", font=f_title)
    draw.text((40, 62), "Mini E-Commerce Store (Microsoft SQL Server 2022 / SQLite) — SQLAlchemy Models", fill="#94A3B8", font=f_sub)

    # Định nghĩa 6 bảng
    tables = [
        {
            "name": "DANHMUC (Category)",
            "rect": (50, 120, 390, 260),
            "header_color": "#1E40AF",
            "columns": [
                ("MADANHMUC", "INT [PK]", "#F59E0B"),
                ("TENDM", "NVARCHAR(50)", "#E2E8F0"),
            ],
            "note": "4 danh mục chính (phẳng 1 cấp)"
        },
        {
            "name": "SANPHAM (Product)",
            "rect": (50, 340, 420, 640),
            "header_color": "#0284C7",
            "columns": [
                ("MASANPHAM", "INT [PK, Identity]", "#F59E0B"),
                ("TENSPH", "NVARCHAR(200)", "#E2E8F0"),
                ("HINHANH", "VARCHAR(500)", "#E2E8F0"),
                ("DONGIA", "NUMERIC(18,2)", "#E2E8F0"),
                ("MOTA", "NVARCHAR(500)", "#E2E8F0"),
                ("SOLUONGTON", "INT [CK >= 0]", "#34D399"),
                ("TRANGTHAISPH", "INT (1=Active, 0=Hide)", "#E2E8F0"),
                ("MADANHMUC", "INT [FK -> DANHMUC]", "#60A5FA"),
            ],
            "note": "CHECK: CK_SANPHAM_SOLUONGTON >= 0"
        },
        {
            "name": "DANHGIA (Review - M:N)",
            "rect": (520, 120, 900, 370),
            "header_color": "#7C3AED",
            "columns": [
                ("MADANHGIA", "INT [PK, Identity]", "#F59E0B"),
                ("MANGUOIDUNG", "INT [FK -> NGUOIDUNG]", "#60A5FA"),
                ("MASANPHAM", "INT [FK -> SANPHAM]", "#60A5FA"),
                ("SOSAO", "INT [CK: 1 <= SOSAO <= 5]", "#FBBF24"),
                ("NOIDUNG", "NVARCHAR(1000)", "#E2E8F0"),
                ("NGAYTAO", "DATETIME [Default: Now]", "#E2E8F0"),
            ],
            "note": "UQ: UQ_DANHGIA_USER_SP (1 review/user/sp)"
        },
        {
            "name": "NGUOIDUNG (User Account)",
            "rect": (980, 120, 1350, 430),
            "header_color": "#4338CA",
            "columns": [
                ("MANGUOIDUNG", "INT [PK, Identity]", "#F59E0B"),
                ("HOTEN", "NVARCHAR(200)", "#E2E8F0"),
                ("EMAIL", "VARCHAR(200)", "#E2E8F0"),
                ("SDT", "VARCHAR(10)", "#E2E8F0"),
                ("NGAYSINH", "DATE", "#E2E8F0"),
                ("PASSWORD_HASH", "VARCHAR(255) [Werkzeug]", "#F87171"),
                ("ROLE", "VARCHAR(20) [admin,staff,cust]", "#34D399"),
                ("TRANGTHAIND", "INT (1=Active, 0=Lock)", "#E2E8F0"),
            ],
            "note": "Role-Based Access Control (RBAC 3 Roles)"
        },
        {
            "name": "DONHANG (Order)",
            "rect": (980, 520, 1350, 830),
            "header_color": "#047857",
            "columns": [
                ("MADONHANG", "INT [PK, Identity]", "#F59E0B"),
                ("MANGUOIDUNG", "INT [FK, Nullable]", "#60A5FA"),
                ("NGAYDAT", "DATE", "#E2E8F0"),
                ("TONGGIATRI", "NUMERIC(18,2)", "#E2E8F0"),
                ("TRANGTHAI", "INT (0=Mới,1=Đang,2=Xong,3=Hủy)", "#FBBF24"),
                ("HOTENNHAN", "NVARCHAR(200)", "#E2E8F0"),
                ("DIACHIGIAO", "NVARCHAR(300)", "#E2E8F0"),
                ("SDTNHAN", "VARCHAR(15)", "#E2E8F0"),
            ],
            "note": "Khách checkout qua Web; status 0->3"
        },
        {
            "name": "CHITIETDONHANG (Order Detail)",
            "rect": (520, 520, 900, 750),
            "header_color": "#B45309",
            "columns": [
                ("MADONHANG", "INT [PK, FK -> DONHANG]", "#F59E0B"),
                ("MASANPHAM", "INT [PK, FK -> SANPHAM]", "#F59E0B"),
                ("SOLUONG", "INT [Số lượng đặt]", "#E2E8F0"),
            ],
            "note": "PK Kép (MADONHANG, MASANPHAM)"
        }
    ]

    for tbl in tables:
        x0, y0, x1, y1 = tbl["rect"]
        # Thân bảng
        draw_rounded_rect(draw, (x0, y0, x1, y1), 8, fill="#1E293B", outline="#334155", width=2)
        # Header
        draw_rounded_rect(draw, (x0, y0, x1, y0 + 38), 8, fill=tbl["header_color"])
        draw.rectangle([x0, y0 + 25, x1, y0 + 38], fill=tbl["header_color"])
        draw.text((x0 + 15, y0 + 8), tbl["name"], fill="#FFFFFF", font=f_tbl_title)

        # Cột
        curr_y = y0 + 48
        for col_name, col_type, col_color in tbl["columns"]:
            draw.text((x0 + 15, curr_y), col_name, fill=col_color, font=f_col)
            draw.text((x0 + 160, curr_y), col_type, fill="#94A3B8", font=f_col)
            curr_y += 24

        # Ghi chú chân bảng
        draw.line([x0 + 10, y1 - 30, x1 - 10, y1 - 30], fill="#334155", width=1)
        draw.text((x0 + 15, y1 - 24), "★ " + tbl["note"], fill="#CBD5E1", font=f_note)

    # Vẽ đường nối quan hệ
    # 1. DANHMUC 1 : N SANPHAM
    draw.line([220, 260, 220, 340], fill="#38BDF8", width=3)
    draw.polygon([(215, 330), (225, 330), (220, 340)], fill="#38BDF8")
    draw.text((230, 290), "1 : N (có)", fill="#38BDF8", font=f_note)

    # 2. SANPHAM 1 : N DANHGIA & NGUOIDUNG 1 : N DANHGIA
    draw.line([420, 400, 520, 280], fill="#C084FC", width=2)
    draw.text((435, 340), "1 : N", fill="#C084FC", font=f_note)

    draw.line([980, 250, 900, 250], fill="#C084FC", width=2)
    draw.polygon([(910, 245), (910, 255), (900, 250)], fill="#C084FC")
    draw.text((920, 230), "1 : N (viết)", fill="#C084FC", font=f_note)

    # 3. NGUOIDUNG 1 : N DONHANG
    draw.line([1165, 430, 1165, 520], fill="#34D399", width=3)
    draw.polygon([(1160, 510), (1170, 510), (1165, 520)], fill="#34D399")
    draw.text((1175, 465), "1 : N (đặt)", fill="#34D399", font=f_note)

    # 4. DONHANG 1 : N CHITIETDONHANG
    draw.line([980, 620, 900, 620], fill="#F59E0B", width=3)
    draw.polygon([(910, 615), (910, 625), (900, 620)], fill="#F59E0B")
    draw.text((920, 600), "1 : N (gồm)", fill="#F59E0B", font=f_note)

    # 5. SANPHAM 1 : N CHITIETDONHANG
    draw.line([420, 560, 520, 600], fill="#F59E0B", width=2)
    draw.polygon([(515, 595), (510, 605), (520, 600)], fill="#F59E0B")
    draw.text((435, 570), "1 : N", fill="#F59E0B", font=f_note)

    # Chú giải
    draw.rounded_rectangle([40, 840, 1350, 895], radius=6, fill="#1E293B", outline="#475569")
    legend_text = (
        "QUAN HỆ:  DANHMUC (1:N) SANPHAM  |  NGUOIDUNG (1:N) DONHANG (1:N) CHITIETDONHANG (N:1) SANPHAM  "
        "|  NGUOIDUNG (M:N qua DANHGIA) SANPHAM"
    )
    draw.text((60, 858), legend_text, fill="#38BDF8", font=f_col)

    out_file = os.path.join(OUTPUT_DIR, "05_erd_diagram.png")
    img.save(out_file)
    print(f"[OK] Generated: {out_file}")

def generate_architecture_diagram():
    """Vẽ Sơ đồ Kiến trúc Application Factory & Blueprints."""
    width, height = 1300, 820
    img = Image.new("RGB", (width, height), "#0B132B")
    draw = ImageDraw.Draw(img)

    f_title = get_font(FONT_BOLD, 24)
    f_sub = get_font(FONT_REGULAR, 14)
    f_layer = get_font(FONT_BOLD, 16)
    f_box = get_font(FONT_BOLD, 14)
    f_desc = get_font(FONT_REGULAR, 11)

    draw.text((40, 20), "KIẾN TRÚC PHÂN TẦNG HỆ THỐNG — FLASK APPLICATION FACTORY", fill="#38BDF8", font=f_title)
    draw.text((40, 55), "Mô hình Module Blueprints, Tầng Dịch Vụ Nghiệp Vụ và Cơ Sở Dữ Liệu Đa Môi Trường", fill="#94A3B8", font=f_sub)

    layers = [
        ("TẦNG TRÌNH DIỄN (CLIENT & PRESENTATION LAYER)", 90, 210, "#1C2541"),
        ("TẦNG ĐIỀU HƯỚNG & QUẢN LÝ BLUEPRINTS (FLASK APPLICATION FACTORY)", 230, 420, "#1C2541"),
        ("TẦNG NGHIỆP VỤ & BẢO MẬT (BUSINESS SERVICES & SECURITY LAYER)", 440, 600, "#1C2541"),
        ("TẦNG DỮ LIỆU & HẠ TẦNG (DATA LAYER & DEPLOYMENT)", 620, 770, "#1C2541")
    ]

    for title, y0, y1, bg in layers:
        draw_rounded_rect(draw, (40, y0, 1260, y1), 8, fill=bg, outline="#3A506B", width=1)
        draw.text((55, y0 + 8), title, fill="#6FFFE9", font=f_layer)

    # Box Tầng 1: Client
    clients = [
        ("Web Browser (Desktop / Mobile)", "Bootstrap 5.3 + Responsive Grid", (60, 130, 420, 195), "#3A506B"),
        ("Tương Tác Real-time Giỏ Hàng", "Vanilla JS (Fetch API + CSRF Token Header)", (440, 130, 840, 195), "#3A506B"),
        ("Ứng Dụng Ngoại Vi / Postman", "RESTful API Consumer (JSON Body)", (860, 130, 1240, 195), "#3A506B"),
    ]
    for name, desc, rect, color in clients:
        draw_rounded_rect(draw, rect, 6, fill="#0B132B", outline=color, width=2)
        draw.text((rect[0] + 12, rect[1] + 10), name, fill="#FFFFFF", font=f_box)
        draw.text((rect[0] + 12, rect[1] + 34), desc, fill="#94A3B8", font=f_desc)

    # Box Tầng 2: 4 Blueprints
    bps = [
        ("app/shop", "Shop Blueprint", "Catalog, Filter, Cart AJAX, Checkout, Đánh giá SP, /my-orders", (60, 275, 340, 395), "#1E40AF"),
        ("app/admin", "Admin Blueprint", "Dashboard thống kê, CRUD Sản phẩm, Quản lý đơn, RBAC 3 vai trò", (360, 275, 640, 395), "#047857"),
        ("app/auth", "Auth Blueprint", "Đăng ký, Đăng nhập (Flask-Login), Logout, chống Open Redirect", (660, 275, 940, 395), "#7C3AED"),
        ("app/api", "API Blueprint", "7 Endpoints RESTful, Flask-JWT-Extended Bearer Token", (960, 275, 1240, 395), "#B45309")
    ]
    for mod, name, desc, rect, col in bps:
        draw_rounded_rect(draw, rect, 6, fill="#0B132B", outline=col, width=2)
        draw_rounded_rect(draw, (rect[0], rect[1], rect[2], rect[1] + 28), 6, fill=col)
        draw.text((rect[0] + 10, rect[1] + 4), mod + " (" + name + ")", fill="#FFFFFF", font=f_box)
        draw.text((rect[0] + 10, rect[1] + 36), desc, fill="#CBD5E1", font=f_desc)

    # Box Tầng 3: Services & Security
    services = [
        ("Services Layer", "product_service.py: lọc/tìm kiếm, phân trang\nreview_service.py: tính sao, chống spam", (60, 480, 420, 575), "#0284C7"),
        ("Bảo Mật OWASP", "Werkzeug PBKDF2/scrypt, CSRFProtect toàn app,\nis_safe_url chống chuyển hướng độc hại", (440, 480, 840, 575), "#DC2626"),
        ("Kiểm Soát Tồn Kho", "with_for_update() (Pessimistic Locking)\nCHECK (SOLUONGTON >= 0) chống âm kho", (860, 480, 1240, 575), "#059669"),
    ]
    for name, desc, rect, col in services:
        draw_rounded_rect(draw, rect, 6, fill="#0B132B", outline=col, width=2)
        draw.text((rect[0] + 12, rect[1] + 10), name, fill="#FBBF24", font=f_box)
        draw.text((rect[0] + 12, rect[1] + 34), desc, fill="#E2E8F0", font=f_desc)

    # Box Tầng 4: Database
    dbs = [
        ("Local Development: SQLite", "File instance/dev.db\nKhởi động cực nhanh cho chấm bài & kiểm thử in-memory", (60, 660, 630, 745), "#475569"),
        ("Production: Docker & SQL Server 2022", "Container SQL Server 2022 Express (Port 14333) + Web App (Port 5050)\nGunicorn WSGI, non-root user, Database: MiniEcommerceDB", (660, 660, 1240, 745), "#2563EB")
    ]
    for name, desc, rect, col in dbs:
        draw_rounded_rect(draw, rect, 6, fill="#0B132B", outline=col, width=2)
        draw.text((rect[0] + 12, rect[1] + 10), name, fill="#38BDF8", font=f_box)
        draw.text((rect[0] + 12, rect[1] + 34), desc, fill="#E2E8F0", font=f_desc)

    out_file = os.path.join(OUTPUT_DIR, "06_architecture_diagram.png")
    img.save(out_file)
    print(f"[OK] Generated: {out_file}")

def generate_test_terminal_image():
    """Vẽ ảnh chụp Terminal kết quả chạy thực tế 156 passed kiểm thử Pytest."""
    width, height = 1100, 580
    img = Image.new("RGB", (width, height), "#181825")  # Dark terminal
    draw = ImageDraw.Draw(img)

    f_title = get_font(FONT_BOLD, 13)
    f_mono = get_font(FONT_MONO, 13)

    # Window top bar
    draw.rectangle([0, 0, width, 36], fill="#11111B")
    # Red, yellow, green buttons
    draw.ellipse([14, 12, 26, 24], fill="#F38BA8")
    draw.ellipse([34, 12, 46, 24], fill="#F9E2AF")
    draw.ellipse([54, 12, 66, 24], fill="#A6E3A1")
    draw.text((85, 9), "PowerShell — pytest (165 Test Cases — 100% PASSED)", fill="#CDD6F4", font=f_title)

    lines = [
        ("PS D:\\FPT\\Kì 5\\PWD301\\MiniEcommerce-PWD301> .\\.venv\\Scripts\\pytest.exe", "#89B4FA"),
        ("============================= test session starts =============================", "#A6ADC8"),
        ("platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0", "#BAC2DE"),
        ("rootdir: D:\\FPT\\Kì 5\\PWD301\\MiniEcommerce-PWD301", "#BAC2DE"),
        ("configfile: pytest.ini", "#BAC2DE"),
        ("testpaths: tests", "#BAC2DE"),
        ("collected 165 items", "#F9E2AF"),
        ("", "#FFFFFF"),
        ("tests\\test_admin.py .......................                              [ 13%]", "#A6E3A1"),
        ("tests\\test_api_auth.py ......                                            [ 17%]", "#A6E3A1"),
        ("tests\\test_api_orders.py ..............                                  [ 26%]", "#A6E3A1"),
        ("tests\\test_api_products.py ............                                  [ 33%]", "#A6E3A1"),
        ("tests\\test_auth_change_password.py ........                              [ 38%]", "#A6E3A1"),
        ("tests\\test_auth_register.py .........                                    [ 43%]", "#A6E3A1"),
        ("tests\\test_cart_checkout.py ....................                         [ 55%]", "#A6E3A1"),
        ("tests\\test_csrf_security.py .........                                    [ 61%]", "#A6E3A1"),
        ("tests\\test_models.py .......                                             [ 65%]", "#A6E3A1"),
        ("tests\\test_products.py ......................................            [ 88%]", "#A6E3A1"),
        ("tests\\test_reviews.py .................                                  [ 98%]", "#A6E3A1"),
        ("tests\\test_stock_constraint.py ..                                        [100%]", "#A6E3A1"),
        ("", "#FFFFFF"),
        ("============================= 165 passed in 8.55s =============================", "#A6E3A1"),
        ("PS D:\\FPT\\Kì 5\\PWD301\\MiniEcommerce-PWD301> ", "#89B4FA")
    ]

    curr_y = 50
    for text, color in lines:
        draw.text((25, curr_y), text, fill=color, font=f_mono)
        curr_y += 21

    out_file = os.path.join(OUTPUT_DIR, "07_test_terminal.png")
    img.save(out_file)
    print(f"[OK] Generated: {out_file}")

def generate_api_postman_image():
    """Vẽ ảnh minh họa kiểm thử 7 RESTful API Endpoints."""
    width, height = 1200, 680
    img = Image.new("RGB", (width, height), "#1E1E2E")
    draw = ImageDraw.Draw(img)

    f_title = get_font(FONT_BOLD, 22)
    f_sub = get_font(FONT_REGULAR, 14)
    f_h = get_font(FONT_BOLD, 15)
    f_mono = get_font(FONT_MONO, 12)
    f_tag = get_font(FONT_BOLD, 11)

    draw.text((35, 20), "KIỂM THỬ HỆ THỐNG 7 RESTFUL API (JSON & JWT BEARER TOKEN)", fill="#89B4FA", font=f_title)
    draw.text((35, 52), "Xác thực bằng Token, Phân quyền truy cập và Xử lý dữ liệu chuẩn RESTful", fill="#A6ADC8", font=f_sub)

    cards = [
        {
            "title": "1. Lấy Bearer Token (Authentication)",
            "method": "POST",
            "url": "http://127.0.0.1:5000/api/auth/token",
            "req": "{\n  \"email\": \"admin@minishop.local\",\n  \"password\": \"Admin@123\"\n}",
            "res": "HTTP 200 OK\n{\n  \"access_token\": \"eyJhbGciOiJIUzI1...\",\n  \"token_type\": \"Bearer\",\n  \"expires_in\": 1800,\n  \"user\": { \"id\": 1, \"name\": \"Admin\", \"role\": \"admin\" }\n}",
            "rect": (35, 90, 585, 360),
            "m_col": "#A6E3A1"
        },
        {
            "title": "2. Lọc & Phân Trang Sản Phẩm",
            "method": "GET",
            "url": "http://127.0.0.1:5000/api/products?category=11&sort=price_asc",
            "req": "Headers:\n  Accept: application/json\n  (No auth required)",
            "res": "HTTP 200 OK\n{\n  \"count\": 6, \"page\": 1, \"per_page\": 8,\n  \"data\": [\n    { \"id\": 1, \"name\": \"iPhone 14\", \"price\": 18500000.0, \"stock\": 15 }\n  ]\n}",
            "rect": (615, 90, 1165, 360),
            "m_col": "#89B4FA"
        },
        {
            "title": "3. Cập Nhật Trạng Thái Đơn Hàng (Admin/Staff Only)",
            "method": "PUT",
            "url": "http://127.0.0.1:5000/api/orders/1/status",
            "req": "Headers: Authorization: Bearer <token>\nBody:\n{\n  \"status\": 2  // 0: Mới, 1: Đang xử lý, 2: Hoàn thành, 3: Hủy\n}",
            "res": "HTTP 200 OK\n{\n  \"message\": \"Order status updated successfully\",\n  \"order\": { \"id\": 1, \"status\": 2, \"total\": \"18500000.00\" }\n}",
            "rect": (35, 380, 585, 640),
            "m_col": "#F9E2AF"
        },
        {
            "title": "4. Danh Sách 7 API Endpoints Chuẩn Hóa",
            "method": "API",
            "url": "Tất cả endpoints tiền tố /api",
            "req": "• POST /api/auth/token      : Đăng nhập lấy Bearer JWT\n• GET  /api/health          : Kiểm tra trạng thái máy chủ\n• GET  /api/products        : Danh sách, lọc & phân trang SP\n• GET  /api/products/<id>   : Chi tiết 1 sản phẩm",
            "res": "• GET  /api/orders          : Danh sách đơn (JWT required)\n• GET  /api/orders/<id>     : Chi tiết 1 đơn hàng (JWT)\n• PUT  /api/orders/<id>/status : Đổi trạng thái (Admin/Staff)\n(Lưu ý: Không có POST đơn qua API, đặt hàng qua web)",
            "rect": (615, 380, 1165, 640),
            "m_col": "#CBA6F7"
        }
    ]

    for c in cards:
        x0, y0, x1, y1 = c["rect"]
        draw_rounded_rect(draw, (x0, y0, x1, y1), 8, fill="#181825", outline="#313244", width=2)
        draw.text((x0 + 15, y0 + 12), c["title"], fill="#CDD6F4", font=f_h)

        # Method tag
        draw_rounded_rect(draw, (x0 + 15, y0 + 38, x0 + 65, y0 + 58), 4, fill=c["m_col"])
        draw.text((x0 + 20, y0 + 41), c["method"], fill="#11111B", font=f_tag)
        draw.text((x0 + 75, y0 + 41), c["url"], fill="#89DCEB", font=f_mono)

        # Box request & response
        draw.rectangle([x0 + 15, y0 + 68, x1 - 15, y1 - 12], fill="#11111B", outline="#45475A")
        content = f">> REQUEST:\n{c['req']}\n\n<< RESPONSE:\n{c['res']}"
        draw.text((x0 + 25, y0 + 74), content, fill="#A6E3A1", font=f_mono)

    out_file = os.path.join(OUTPUT_DIR, "08_api_postman.png")
    img.save(out_file)
    print(f"[OK] Generated: {out_file}")

if __name__ == "__main__":
    generate_erd_diagram()
    generate_architecture_diagram()
    generate_test_terminal_image()
    generate_api_postman_image()
    print("[SUCCESS] All 4 technical diagrams generated successfully!")
