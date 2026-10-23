# -*- coding: utf-8 -*-
"""
Script tạo tài liệu báo cáo đồ án Word (.docx) gọn gàng, súc tích và dễ hiểu:
Đề tài: Topic 8 - Mini E-Commerce Store (Môn học PWD301 - FPT University).
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Đặt màu nền cho ô trong bảng."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt lề padding cho ô (dxa: 20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    """Đặt đường viền thanh mảnh cho bảng."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_concise_document():
    doc = docx.Document()

    # 1. Khổ giấy A4, căn lề 0.8 inch cho thoáng và gọn
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    # 2. Bảng màu chủ đạo sang trọng & chuyên nghiệp
    color_primary = RGBColor(30, 58, 138)    # Xanh Navy đậm (#1E3A8A)
    color_secondary = RGBColor(37, 99, 235)  # Xanh Dương tươi (#2563EB)
    color_dark = RGBColor(31, 41, 55)        # Màu chữ than đậm (#1F2937)
    color_gray = RGBColor(75, 85, 99)        # Xám phụ đề (#4B5563)

    # Cấu hình Style mặc định
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = color_dark
    style_normal.paragraph_format.line_spacing = 1.2
    style_normal.paragraph_format.space_after = Pt(4)

    # Helper: Tiêu đề H1
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(15)
        r.bold = True
        r.font.color.rgb = color_primary
        return p

    # Helper: Tiêu đề H2
    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(12)
        r.bold = True
        r.font.color.rgb = color_secondary
        return p

    # Helper: Hộp ghi chú / Callout
    def add_callout(title, text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.rows[0].cells[0]
        cell.width = Inches(6.67)
        set_cell_background(cell, "F0F7FF")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="18" w:space="0" w:color="2563EB"/>'
            f'  <w:top w:val="none"/>'
            f'  <w:bottom w:val="none"/>'
            f'  <w:right w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        r_t = p.add_run(title + ": ")
        r_t.bold = True
        r_t.font.color.rgb = color_secondary
        r_m = p.add_run(text)
        r_m.font.color.rgb = color_dark
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Helper: Hộp mã lệnh / Code Box
    def add_code(text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.rows[0].cells[0]
        cell.width = Inches(6.67)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
            f'  <w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.1
        r = p.add_run(text)
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Helper: Bảng dữ liệu gọn gàng
    def add_table(headers, rows_data, col_widths=None):
        table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Dòng tiêu đề
        header_row = table.rows[0]
        for idx, text in enumerate(headers):
            cell = header_row.cells[idx]
            if col_widths and idx < len(col_widths):
                cell.width = Inches(col_widths[idx])
            set_cell_background(cell, "1E3A8A")
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            r.font.size = Pt(9.5)

        # Các dòng dữ liệu
        for r_idx, row_values in enumerate(rows_data):
            row = table.rows[r_idx + 1]
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_values):
                cell = row.cells[c_idx]
                if col_widths and c_idx < len(col_widths):
                    cell.width = Inches(col_widths[c_idx])
                set_cell_background(cell, bg_color)
                set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                r = p.add_run(str(val))
                r.font.size = Pt(9)
                r.font.color.rgb = color_dark

        set_table_borders(table, color="CBD5E1", sz="4")
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return table

    # ==================== TRANG BÌA ====================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_inst.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO — TRƯỜNG ĐẠI HỌC FPT\n")
    r_uni.bold = True
    r_uni.font.size = Pt(11.5)
    r_uni.font.color.rgb = color_primary
    r_dept = p_inst.add_run("KHOA CÔNG NGHỆ THÔNG TIN — BỘ MÔN KỸ THUẬT PHẦN MỀM\n")
    r_dept.bold = True
    r_dept.font.size = Pt(10.5)
    r_dept.font.color.rgb = color_gray

    doc.add_paragraph("\n")

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run("BÁO CÁO TỔNG KẾT ĐỒ ÁN MÔN HỌC PWD301\n")
    r_sub.font.size = Pt(13)
    r_sub.bold = True
    r_sub.font.color.rgb = color_secondary

    r_main = p_title.add_run("ĐỀ TÀI: TOPIC 8 — MINI E-COMMERCE STORE\n")
    r_main.font.size = Pt(20)
    r_main.bold = True
    r_main.font.color.rgb = color_primary

    r_desc = p_title.add_run("Hệ Thống Website Cửa Hàng Trực Tuyến Thu Nhỏ với Python Flask & SQL Server")
    r_desc.font.size = Pt(11)
    r_desc.italic = True
    r_desc.font.color.rgb = color_gray

    doc.add_paragraph("\n")

    # Bảng thông tin nhóm ngắn gọn
    tbl_cover = doc.add_table(rows=5, cols=2)
    tbl_cover.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cover.autofit = False

    cover_info = [
        ("Môn học:", "PWD301 — Lập trình ứng dụng Web với Python (Web App Development with Python)"),
        ("Đề tài chỉ định:", "Topic 8: Mini E-Commerce Store"),
        ("Nhóm sinh viên:", "Châu Lê Gia Bảo (Nhóm trưởng) • Hà Trung Kiên • Trần Vũ Hoàng Long • Minh Tuấn"),
        ("Công nghệ chính:", "Python 3.12, Flask 3.1, SQL Server 2022 / SQLite, Docker, JWT, AJAX"),
        ("Thời gian thực hiện:", "Học kỳ 5 (Năm học 2025 – 2026)")
    ]

    for idx, (label, val) in enumerate(cover_info):
        row = tbl_cover.rows[idx]
        cell_l, cell_r = row.cells[0], row.cells[1]
        cell_l.width = Inches(1.8)
        cell_r.width = Inches(4.87)

        p_l = cell_l.paragraphs[0]
        r_l = p_l.add_run(label)
        r_l.bold = True
        r_l.font.size = Pt(9.5)
        r_l.font.color.rgb = color_primary

        p_r = cell_r.paragraphs[0]
        r_r = p_r.add_run(val)
        r_r.font.size = Pt(9.5)
        r_r.font.color.rgb = color_dark

        set_cell_background(cell_l, "F8FAFC")
        set_cell_background(cell_r, "F8FAFC")
        set_cell_margins(cell_l, top=60, bottom=60, left=80, right=80)
        set_cell_margins(cell_r, top=60, bottom=60, left=80, right=80)

    set_table_borders(tbl_cover, color="CBD5E1", sz="4")

    doc.add_page_break()

    # ==================== PHẦN 1 ====================
    add_h1("PHẦN 1: MỤC TIÊU ĐỀ TÀI")

    p = doc.add_paragraph()
    p.add_run(
        "Đề tài Topic 8 (Mini E-Commerce Store) nhằm xây dựng một hệ thống website bán hàng trực tuyến "
        "hoàn chỉnh, hiện đại và chuẩn công nghiệp, đáp ứng đầy đủ chuẩn đầu ra môn học PWD301. "
        "Hệ thống mô phỏng một cửa hàng chuyên doanh công nghệ và thời trang với luồng nghiệp vụ khép kín từ xem hàng, "
        "tìm kiếm/lọc, giỏ hàng tương tác thời gian thực, đặt hàng, quản lý đơn hàng cho đến đánh giá sản phẩm."
    )

    add_h2("1.1. Các mục tiêu trọng tâm cần đạt được")
    objectives = [
        ("Nghiệp vụ thương mại điện tử trọn vẹn: ", "Cung cấp đầy đủ luồng mua sắm gồm duyệt danh mục, tìm kiếm, lọc giá đa tiêu chí, giỏ hàng real-time, thanh toán COD, quản lý lịch sử đơn hàng và đánh giá sản phẩm."),
        ("Tương tác mượt mà bằng AJAX: ", "Cập nhật giỏ hàng tức thời (thêm, tăng/giảm số lượng, xóa món) mà không cần tải lại toàn bộ trang web (Fetch API không reload)."),
        ("Xử lý giao dịch an toàn (Chống bán âm kho): ", "Ứng dụng cơ chế khóa bi quan (Pessimistic Locking - with_for_update) và transaction nguyên tử trong SQLAlchemy để ngăn chặn tuyệt đối lỗi race condition khi nhiều người cùng mua sản phẩm cuối."),
        ("Bảo mật chuẩn OWASP: ", "Mật khẩu mã hóa Bcrypt một chiều an toàn; kích hoạt CSRF Token tự động trên mọi form state-changing; auto-escaping chống XSS; phân quyền chặt chẽ (RBAC) giữa Khách hàng và Quản trị viên."),
        ("Cung cấp RESTful API có JWT: ", "Xây dựng 7 endpoints API hoàn chỉnh có xác thực qua JSON Web Token (Bearer Token), sẵn sàng tích hợp với Mobile App hoặc bên thứ ba."),
        ("Kiểm thử & Triển khai chuẩn hóa: ", "Hỗ trợ 2 chế độ cơ sở dữ liệu linh hoạt (SQLite cho Local và SQL Server 2022 cho Docker); 100% kiểm thử tự động với 144/144 test cases passed.")
    ]
    for bold_text, normal_text in objectives:
        p_item = doc.add_paragraph(style='List Bullet')
        p_item.paragraph_format.space_after = Pt(2)
        r_b = p_item.add_run(bold_text)
        r_b.bold = True
        r_b.font.color.rgb = color_primary
        p_item.add_run(normal_text)

    # ==================== PHẦN 2 ====================
    add_h1("PHẦN 2: THÀNH PHẦN ĐỀ TÀI & THIẾT KẾ KIẾN TRÚC")

    add_h2("2.1. Ngăn xếp công nghệ (Technology Stack)")
    tech_data = [
        ("Back-end Framework", "Python 3.12 + Flask 3.1.3", "Mô hình Application Factory (create_app), chia Blueprints độc lập"),
        ("Cơ sở dữ liệu", "SQL Server 2022 & SQLite", "SQL Server cho Docker Production; SQLite cho phát triển Local nhẹ nhàng"),
        ("Thư viện ORM & Di trú", "Flask-SQLAlchemy + Alembic", "Truy vấn ORM an toàn (tránh SQLi), quản lý migration phiên bản CSDL"),
        ("Xác thực & Bảo mật", "Flask-Login, Flask-WTF, JWT", "Bcrypt hash mật khẩu, CSRF token bắt buộc, JWT Bearer Token cho API"),
        ("Front-end", "Jinja2, Bootstrap 5.3, Vanilla JS", "Giao diện Glassmorphism hiện đại, responsive mobile, Fetch API cho giỏ hàng"),
        ("Kiểm thử tự động", "Pytest (144 Test Cases)", "Bảo đảm 100% luồng nghiệp vụ, kiểm tra đồng thời và phân quyền")
    ]
    add_table(["Thành phần", "Công nghệ sử dụng", "Mô tả vai trò"], tech_data, [1.5, 2.0, 3.17])

    add_h2("2.2. Cấu trúc mô-đun dự án (Application Factory Pattern)")
    p_arch = doc.add_paragraph()
    p_arch.add_run(
        "Mã nguồn được phân tách theo kiến trúc mở rộng chuẩn công nghiệp với 4 Blueprints độc lập:"
    )
    blueprints = [
        ("app/blueprints/shop: ", "Xử lý toàn bộ giao diện khách hàng (trang chủ, xem/tìm kiếm sản phẩm, giỏ hàng session/database, checkout, xem lịch sử đơn, đánh giá sản phẩm)."),
        ("app/blueprints/admin: ", "Dành riêng cho Quản trị viên (@admin_required): Dashboard thống kê doanh thu/tồn kho, CRUD sản phẩm, cập nhật trạng thái đơn hàng."),
        ("app/blueprints/auth: ", "Xử lý đăng ký, đăng nhập (Flask-Login session), đổi mật khẩu và đăng xuất."),
        ("app/blueprints/api: ", "Cung cấp các API RESTful JSON xác thực bằng JWT cho các ứng dụng ngoại vi.")
    ]
    for b_title, b_desc in blueprints:
        p_bp = doc.add_paragraph(style='List Bullet')
        p_bp.paragraph_format.space_after = Pt(2)
        r_bt = p_bp.add_run(b_title)
        r_bt.bold = True
        p_bp.add_run(b_desc)

    add_h2("2.3. Cơ sở dữ liệu (6 bảng dữ liệu chuẩn hóa)")
    db_data = [
        ("NGUOIDUNG", "MAND (PK), HOTEN, EMAIL (Unique), PASSWORD_HASH, ROLE, TRANGTHAIND", "Lưu tài khoản phân quyền: 'admin' và 'customer'. Mật khẩu mã hóa Bcrypt."),
        ("DANHMUC", "MADANHMUC (PK), TENDM, MOTA", "4 danh mục: Điện thoại (11), Laptop (12), Thời trang nam (21), Thời trang nữ (22)."),
        ("SANPHAM", "MASANPHAM (PK), TENSPH, HINHANH, DONGIA, MOTA, SOLUONGTON, MADANHMUC (FK)", "23 sản phẩm thực tế kèm ảnh rõ nét, quản lý số lượng tồn kho và trạng thái."),
        ("DONHANG", "MADONHANG (PK), MAND (FK), NGAYDAT, TONGTIEN, TRANGTHAI, DIACHIGIAO, SODIENTHOAI", "Quản lý đơn hàng: 'cho_xu_ly', 'dang_giao', 'da_giao', 'da_huy'."),
        ("CHITIETDONHANG", "MACHITIET (PK), MADONHANG (FK), MASANPHAM (FK), SOLUONG, DONGIA", "Chi tiết các sản phẩm trong đơn, lưu lại đơn giá cố định tại thời điểm đặt."),
        ("DANHGIA", "MADANHGIA (PK), MAND (FK), MASANPHAM (FK), SOSAO (1-5), BINHLUAN, NGAYDANHGIA", "Quan hệ M:N giữa Người dùng và Sản phẩm, tự động tính điểm sao trung bình.")
    ]
    add_table(["Tên Bảng", "Cột chính & Khóa", "Ý nghĩa nghiệp vụ"], db_data, [1.4, 2.5, 2.77])

    add_h2("2.4. Danh sách tính năng cốt lõi")
    features_data = [
        ("Duyệt & Tìm kiếm", "Khách hàng", "Tìm kiếm theo từ khóa tên/mô tả; lọc theo danh mục; lọc giá Min-Max; sắp xếp giá tăng/giảm hoặc mới nhất; phân trang 8 SP/trang."),
        ("Giỏ hàng Real-time", "Khách hàng", "Thêm sản phẩm, tăng giảm số lượng, xóa dòng sản phẩm tức thời bằng AJAX Fetch API, tự tính tổng tiền không cần reload trang."),
        ("Đặt hàng & Trừ kho", "Khách hàng", "Đặt hàng COD, tự động kiểm tra tồn kho bằng transaction khóa bi quan, trừ kho an toàn, báo lỗi nếu kho không đủ."),
        ("Đánh giá sản phẩm", "Khách hàng", "Cho phép người dùng đã đăng nhập chấm điểm từ 1 đến 5 sao và viết nhận xét; hiển thị số sao trung bình trên từng sản phẩm."),
        ("Dashboard Admin", "Admin", "Xem thống kê tổng quan: Doanh thu thực tế, số đơn hoàn tất, tổng người dùng, danh sách cảnh báo sản phẩm sắp hết hàng (tồn <= 5)."),
        ("Quản lý sản phẩm", "Admin", "Thực hiện CRUD sản phẩm: Thêm mới, cập nhật giá/tồn kho/mô tả/ảnh, ẩn sản phẩm khi ngừng kinh doanh."),
        ("Quản lý đơn hàng", "Admin", "Xem chi tiết người mua, các món hàng trong đơn, chuyển trạng thái đơn (Chờ xử lý -> Đang giao -> Đã giao / Đã hủy)."),
        ("Hệ thống 7 REST API", "Hệ thống", "POST /api/auth/login (lấy JWT); GET /api/products; GET /api/products/<id>; GET & POST /api/orders; GET /api/health.")
    ]
    add_table(["Tính năng", "Phân quyền", "Mô tả chi tiết"], features_data, [1.4, 1.1, 4.17])

    # ==================== PHẦN 3 ====================
    add_h1("PHẦN 3: HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG")

    add_h2("3.1. Cách 1: Chạy trực tiếp trên máy với SQLite (Nhanh nhất cho Demo / Chấm bài)")
    p_run1 = doc.add_paragraph()
    p_run1.add_run("Phương thức này sử dụng SQLite có sẵn trong Python, khởi động cực nhanh chỉ qua 3 bước:")

    add_code(
        "# Bước 1: Mở terminal tại thư mục dự án và kích hoạt môi trường ảo (Virtualenv)\n"
        ".\\.venv\\Scripts\\activate          # Trên Windows PowerShell / CMD\n"
        "# hoặc: source .venv/bin/activate    # Trên macOS / Linux\n\n"
        "# Bước 2: Cài đặt các thư viện cần thiết (nếu chưa cài)\n"
        "pip install -r requirements.txt\n\n"
        "# Bước 3: Khởi chạy máy chủ phát triển Flask\n"
        "python run.py\n\n"
        "# -> Truy cập trình duyệt web tại địa chỉ: http://127.0.0.1:5000"
    )

    add_h2("3.2. Cách 2: Chạy chuẩn hóa môi trường bằng Docker (SQL Server 2022)")
    p_run2 = doc.add_paragraph()
    p_run2.add_run(
        "Dành cho môi trường sản xuất (Production), tự động khởi tạo đồng thời container Web Flask "
        "và container Microsoft SQL Server 2022:"
    )

    add_code(
        "# Chạy toàn bộ hệ thống Web + SQL Server bằng Docker Compose:\n"
        "docker-compose up --build -d\n\n"
        "# -> Truy cập ứng dụng tại: http://localhost:5000\n"
        "# Để tắt hệ thống khi dừng kiểm tra:\n"
        "docker-compose down"
    )

    add_h2("3.3. Danh sách tài khoản thử nghiệm có sẵn (Demo Accounts)")
    account_data = [
        ("Quản trị viên (Admin)", "admin@minishop.local", "Admin@123", "Toàn quyền: Dashboard thống kê, quản lý sản phẩm, duyệt đơn hàng"),
        ("Khách hàng (Customer)", "customer@minishop.local", "Customer@123", "Quyền mua hàng: Giỏ hàng, đặt hàng, xem đơn của mình, viết đánh giá")
    ]
    add_table(["Vai trò", "Email đăng nhập", "Mật khẩu", "Quyền hạn & Chức năng"], account_data, [1.5, 1.8, 1.2, 2.17])

    add_h2("3.4. Chạy bộ kiểm thử tự động (Automated Testing với Pytest)")
    p_test = doc.add_paragraph()
    p_test.add_run(
        "Dự án tích hợp bộ 144 bài test tự động bao quát toàn bộ bảo mật CSRF, giao dịch tồn kho, "
        "quy trình giỏ hàng, đặt hàng, phân quyền admin và REST API:"
    )

    add_code(
        "# Chạy toàn bộ bộ kiểm thử tự động:\n"
        "pytest\n\n"
        "# Kết quả xác thực: 144 passed in 5.8s (100% PASSED)"
    )

    # ==================== PHẦN 4 ====================
    add_h1("PHẦN 4: TỔNG KẾT & ĐÁNH GIÁ ĐỀ TÀI")

    add_h2("4.1. Kết quả đạt được so với yêu cầu đề tài")
    summary_eval = [
        ("Kiến trúc chuẩn", "Đạt 100%", "Áp dụng Application Factory, Blueprints phân tầng rõ ràng, code sạch dễ bảo trì."),
        ("Giao diện & Trải nghiệm", "Đạt 100%", "Giao diện hiện đại, hình ảnh sản phẩm thực tế, giỏ hàng AJAX không reload."),
        ("Xử lý tồn kho an toàn", "Đạt 100%", "Áp dụng khóa bi quan (with_for_update), không bao giờ bị âm kho khi mua đồng thời."),
        ("Bảo mật đa tầng", "Đạt 100%", "Bcrypt hashing, bắt buộc CSRF token, chống XSS, RBAC chuẩn xác."),
        ("REST API & JWT", "Đạt 100%", "7 endpoints chuẩn RESTful, có Bearer Token, kiểm tra trạng thái Health Check."),
        ("Kiểm thử tự động", "Đạt 100%", "144 bài kiểm thử Pytest chạy độc lập với cơ sở dữ liệu in-memory, pass 100%.")
    ]
    add_table(["Tiêu chí đánh giá", "Mức độ hoàn thành", "Ghi chú kết quả thực tế"], summary_eval, [1.8, 1.4, 3.47])

    add_h2("4.2. Hướng phát triển trong tương lai")
    next_steps = [
        ("Tích hợp cổng thanh toán trực tuyến: ", "Mở rộng kết nối API cổng thanh toán VNPay, MoMo hoặc ZaloPay để thanh toán qua mã QR."),
        ("Ứng dụng di động (Mobile App): ", "Kết nối với app Flutter hoặc React Native thông qua 7 REST API JWT đã hoàn thiện."),
        ("Gợi ý sản phẩm thông minh: ", "Ứng dụng Machine Learning để gợi ý các sản phẩm cùng sở thích dựa trên lịch sử mua sắm.")
    ]
    for b_step, n_step in next_steps:
        p_s = doc.add_paragraph(style='List Bullet')
        p_s.paragraph_format.space_after = Pt(2)
        r_sb = p_s.add_run(b_step)
        r_sb.bold = True
        p_s.add_run(n_step)

    add_callout(
        "KẾT LUẬN CHUNG",
        "Đề tài Topic 8 (Mini E-Commerce Store) đã được nhóm hoàn thiện toàn diện về mặt kỹ thuật, "
        "nghiệp vụ và bảo mật. Dự án chạy mượt mà, cấu trúc mã nguồn chỉn chu, sẵn sàng để bảo vệ và bàn giao môn học PWD301."
    )

    # Lưu tài liệu Word
    output_path = os.path.abspath("Bao_Cao_De_Tai_Topic_8_MiniEcommerce.docx")
    doc.save(output_path)
    print(f"[SUCCESS] Saved concise report to: {output_path}")

if __name__ == "__main__":
    build_concise_document()
