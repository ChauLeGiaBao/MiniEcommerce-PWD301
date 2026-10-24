# -*- coding: utf-8 -*-
"""
Script tạo tài liệu báo cáo đồ án Word (.docx) chuyên nghiệp, chuẩn xác và toàn diện:
Đề tài: Topic 8 - Mini E-Commerce Store (Môn học PWD301 - FPT University).
Báo cáo đối chiếu chuẩn 100% với mã nguồn GitHub ChauLeGiaBao/MiniEcommerce-PWD301.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "docs", "screenshots")

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

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
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

def build_comprehensive_document():
    doc = docx.Document()

    # 1. Khổ giấy A4, căn lề 0.75 inch
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    # 2. Bảng màu chủ đạo thanh lịch
    color_primary = RGBColor(30, 58, 138)    # Xanh Navy đậm (#1E3A8A)
    color_secondary = RGBColor(37, 99, 235)  # Xanh Dương tươi (#2563EB)
    color_dark = RGBColor(31, 41, 55)        # Màu chữ than đậm (#1F2937)
    color_gray = RGBColor(75, 85, 99)        # Xám phụ đề (#4B5563)

    # Style mặc định
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = color_dark
    style_normal.paragraph_format.line_spacing = 1.2
    style_normal.paragraph_format.space_after = Pt(4)

    # Helper: Tiêu đề H1
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(15)
        r.bold = True
        r.font.color.rgb = color_primary
        return p

    # Helper: Tiêu đề H2
    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(11)
        p.paragraph_format.space_after = Pt(4)
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
        cell.width = Inches(6.77)
        set_cell_background(cell, "F0F7FF")
        set_cell_margins(cell, top=90, bottom=90, left=140, right=140)

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
        cell.width = Inches(6.77)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=70, bottom=70, left=110, right=110)

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
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(30, 41, 59)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Helper: Bảng dữ liệu chuẩn mực
    def add_table(headers, rows_data, col_widths=None):
        table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        header_row = table.rows[0]
        for idx, text in enumerate(headers):
            cell = header_row.cells[idx]
            if col_widths and idx < len(col_widths):
                cell.width = Inches(col_widths[idx])
            set_cell_background(cell, "1E3A8A")
            set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            r.font.size = Pt(9.0)

        for r_idx, row_values in enumerate(rows_data):
            row = table.rows[r_idx + 1]
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_values):
                cell = row.cells[c_idx]
                if col_widths and c_idx < len(col_widths):
                    cell.width = Inches(col_widths[c_idx])
                set_cell_background(cell, bg_color)
                set_cell_margins(cell, top=55, bottom=55, left=90, right=90)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.12
                r = p.add_run(str(val))
                r.font.size = Pt(8.5)
                r.font.color.rgb = color_dark

        set_table_borders(table, color="CBD5E1", sz="4")
        doc.add_paragraph().paragraph_format.space_after = Pt(3)
        return table

    # Helper: Chèn hình ảnh kèm chú thích
    def add_image_with_caption(filename, caption, width_inches=6.2):
        img_path = os.path.join(SCREENSHOTS_DIR, filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(2)
            run = p_img.add_run()
            run.add_picture(img_path, width=Inches(width_inches))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(0)
            p_cap.paragraph_format.space_after = Pt(6)
            r_c = p_cap.add_run(f"★ {caption}")
            r_c.font.size = Pt(8.5)
            r_c.font.italic = True
            r_c.font.color.rgb = color_gray
        else:
            print(f"[WARN] Image file not found: {img_path}")

    # ==================== TRANG BÌA ====================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_inst.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO — TRƯỜNG ĐẠI HỌC FPT\n")
    r_uni.bold = True
    r_uni.font.size = Pt(11.5)
    r_uni.font.color.rgb = color_primary
    r_dept = p_inst.add_run("KHOA CÔNG NGHỆ THÔNG TIN — BỘ MÔN KỸ THUẬT PHẦN MỀM\n")
    r_dept.bold = True
    r_dept.font.size = Pt(10.0)
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

    r_desc = p_title.add_run("Hệ Thống Website Cửa Hàng Trực Tuyến Thu Nhỏ với Python Flask & Microsoft SQL Server 2022")
    r_desc.font.size = Pt(11)
    r_desc.italic = True
    r_desc.font.color.rgb = color_gray

    doc.add_paragraph("\n")

    tbl_cover = doc.add_table(rows=6, cols=2)
    tbl_cover.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cover.autofit = False

    cover_info = [
        ("Môn học:", "PWD301 — Lập trình ứng dụng Web với Python (Web App Development with Python)"),
        ("Đề tài chỉ định:", "Topic 8: Mini E-Commerce Store"),
        ("Nhóm sinh viên thực hiện:", "Châu Lê Gia Bảo (Nhóm trưởng) • Hà Trung Kiên • Trần Vũ Hoàng Long • Minh Tuấn"),
        ("Công nghệ chính:", "Python 3.12, Flask 3.1.3, SQLAlchemy 2.0, SQL Server 2022 / SQLite, Docker, JWT, AJAX"),
        ("Thời gian thực hiện:", "Học kỳ Fall 2026 (Học kỳ 5 — Năm học 2026 – 2027)"),
        ("Kho lưu trữ mã nguồn:", "GitHub: ChauLeGiaBao/MiniEcommerce-PWD301 (Nhánh main)")
    ]

    for idx, (label, val) in enumerate(cover_info):
        row = tbl_cover.rows[idx]
        cell_l, cell_r = row.cells[0], row.cells[1]
        cell_l.width = Inches(2.0)
        cell_r.width = Inches(4.77)

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
        set_cell_margins(cell_l, top=55, bottom=55, left=70, right=70)
        set_cell_margins(cell_r, top=55, bottom=55, left=70, right=70)

    set_table_borders(tbl_cover, color="CBD5E1", sz="4")
    doc.add_page_break()

    # ==================== MỤC LỤC TỔNG QUAN ====================
    add_h1("MỤC LỤC TỔNG QUAN BÁO CÁO")
    toc_items = [
        ("PHẦN 1: MỤC TIÊU ĐỀ TÀI & NGHIỆP VỤ CỐT LÕI", "Trang 2"),
        ("PHẦN 2: THIẾT KẾ KIẾN TRÚC & CƠ SỞ DỮ LIỆU", "Trang 2"),
        ("    2.1. Ngăn xếp công nghệ chi tiết (Technology Stack)", "Trang 2"),
        ("    2.2. Kiến trúc Application Factory & Phân hệ Blueprints", "Trang 3"),
        ("    2.3. Thiết kế Cơ sở dữ liệu chuẩn hóa (6 Bảng & Ràng buộc)", "Trang 4"),
        ("    2.4. Danh mục Tính năng cốt lõi & Hệ thống 7 RESTful API", "Trang 5"),
        ("PHẦN 3: GIAO DIỆN NGƯỜI DÙNG & MINH CHỨNG THỰC NGHIỆM", "Trang 6"),
        ("PHẦN 4: HƯỚNG DẪN CÀI ĐẶT & TRIỂN KHAI HỆ THỐNG", "Trang 7"),
        ("    4.1. Cách 1: Chạy trực tiếp với SQLite (Local Testing / Demo)", "Trang 7"),
        ("    4.2. Cách 2: Triển khai Docker Compose & SQL Server 2022 (Port 5050)", "Trang 7"),
        ("    4.3. Bảng tài khoản thử nghiệm có sẵn (Demo Accounts - 3 Roles)", "Trang 8"),
        ("    4.4. Bộ kiểm thử tự động Pytest (156 Test Cases Passed)", "Trang 8"),
        ("PHẦN 5: PHÂN CÔNG CÔNG VIỆC & QUY TRÌNH PHÁT TRIỂN", "Trang 9"),
        ("PHẦN 6: ĐÁNH GIÁ KẾT QUẢ, HẠN CHẾ & HƯỚNG PHÁT TRIỂN", "Trang 10"),
        ("PHỤ LỤC A: NHẬT KÝ SỬ DỤNG AI CÓ TRÁCH NHIỆM (AI USAGE LOG)", "Trang 11"),
        ("PHỤ LỤC B: TÀI LIỆU THAM KHẢO & QUY CHUẨN KỸ THUẬT", "Trang 12")
    ]
    for title, pg in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_after = Pt(2)
        r_t = p_toc.add_run(title)
        if "PHẦN" in title or "PHỤ LỤC" in title:
            r_t.bold = True
            r_t.font.color.rgb = color_primary
        else:
            r_t.font.color.rgb = color_dark
        p_toc.add_run(" " + "." * max(10, 85 - len(title)) + " " + pg)

    doc.add_page_break()

    # ==================== PHẦN 1 ====================
    add_h1("PHẦN 1: MỤC TIÊU ĐỀ TÀI & NGHIỆP VỤ CỐT LÕI")
    p_p1 = doc.add_paragraph()
    p_p1.add_run(
        "Đề tài Topic 8 (Mini E-Commerce Store) tập trung hiện thực một hệ thống bán hàng trực tuyến thu nhỏ "
        "dựa trên nền tảng ngôn ngữ Python và framework Flask, kết nối cơ sở dữ liệu quan hệ Microsoft SQL Server 2022 "
        "và SQLite. Hệ thống hoàn chỉnh luồng nghiệp vụ mua sắm từ duyệt danh mục, tìm kiếm, lọc giá đa tiêu chí, "
        "quản lý giỏ hàng bất đồng bộ (AJAX), thanh toán an toàn chống âm kho, lịch sử đơn hàng cho đến đánh giá sản phẩm."
    )

    add_h2("1.1. Các mục tiêu kỹ thuật trọng tâm")
    objectives = [
        ("Nghiệp vụ thương mại điện tử trọn vẹn: ", "Cung cấp đầy đủ luồng mua sắm gồm duyệt danh mục, tìm kiếm từ khóa không phân biệt hoa thường, lọc giá đa tiêu chí, giỏ hàng real-time, thanh toán COD, quản lý lịch sử đơn cá nhân (/my-orders) và gửi nhận xét đánh giá sản phẩm."),
        ("Tương tác mượt mà bằng AJAX: ", "Cập nhật giỏ hàng tức thời (thêm món, tăng/giảm số lượng, xóa sản phẩm) thông qua Fetch API trong cart.js mà không cần tải lại toàn bộ trang web (Zero Page Reload), tự động gửi kèm X-CSRFToken header."),
        ("Xử lý giao dịch an toàn (Chống bán âm kho): ", "Ứng dụng cơ chế khóa bi quan (Pessimistic Locking - with_for_update) trên SQL Server kết hợp lớp bảo vệ thứ hai bằng ràng buộc cơ sở dữ liệu CHECK (SOLUONGTON >= 0) và transaction nguyên tử trong SQLAlchemy."),
        ("Bảo mật đa tầng theo tiêu chuẩn OWASP: ", "Mật khẩu băm an toàn bằng thư viện Werkzeug (thuật toán PBKDF2:SHA256/scrypt); CSRFProtect kích hoạt trên toàn bộ các biểu mẫu state-changing; auto-escaping chống XSS; kiểm tra an toàn URL chống Open Redirect (is_safe_url); cookie bảo mật HttpOnly."),
        ("Phân quyền 3 vai trò (RBAC): ", "Phân định quyền hạn rõ ràng giữa Quản trị viên (Admin), Nhân viên vận hành (Staff) và Khách hàng (Customer) thông qua Flask-Login và bộ lọc before_request."),
        ("Cung cấp 7 RESTful API chuẩn JSON có JWT: ", "Hệ thống xây dựng 7 API endpoints hoàn chỉnh có xác thực qua JSON Web Token (Bearer Token), kiểm tra trạng thái tài khoản trực tiếp từ database trước khi cấp quyền."),
        ("Hỗ trợ đa môi trường & Kiểm thử tự động: ", "Vận hành linh hoạt trên 2 môi trường (SQLite cho Local dev/chấm bài và SQL Server 2022 qua Docker Compose cổng 5050); xác thực bằng bộ kiểm thử tự động gồm 156/156 test cases passed.")
    ]
    for bold_text, normal_text in objectives:
        p_item = doc.add_paragraph(style='List Bullet')
        p_item.paragraph_format.space_after = Pt(2)
        r_b = p_item.add_run(bold_text)
        r_b.bold = True
        r_b.font.color.rgb = color_primary
        p_item.add_run(normal_text)

    # ==================== PHẦN 2 ====================
    add_h1("PHẦN 2: THIẾT KẾ KIẾN TRÚC & CƠ SỞ DỮ LIỆU")

    add_h2("2.1. Ngăn xếp công nghệ chi tiết (Technology Stack)")
    tech_data = [
        ("Back-end Framework", "Python 3.12 + Flask 3.1.3", "Mô hình Application Factory (create_app), chia 4 Blueprints độc lập"),
        ("Cơ sở dữ liệu chính", "SQL Server 2022 Express", "Chạy trong Docker container (Port 14333, DB: MiniEcommerceDB) với ODBC Driver 18"),
        ("Cơ sở dữ liệu phát triển", "SQLite 3 (instance/dev.db)", "Phục vụ chạy test nhanh, phát triển local và chấm bài không cần cài Docker"),
        ("ORM & Quản lý Migration", "Flask-SQLAlchemy 3.1 + Alembic", "Truy vấn hướng đối tượng tránh SQL Injection; 5 phiên bản migration lịch sử"),
        ("Xác thực & Quản trị phiên", "Flask-Login 0.6.3", "Quản lý phiên đăng nhập người dùng, UserMixin, bảo vệ session bằng cookie HttpOnly"),
        ("Mã hóa mật khẩu", "Werkzeug Security 3.1.8", "Hàm generate_password_hash / check_password_hash với chuẩn PBKDF2:SHA256"),
        ("Bảo mật API (JWT)", "Flask-JWT-Extended 4.7.1", "Tạo và kiểm tra JWT Bearer Token, kiểm tra trực tiếp user từ DB tại mỗi request"),
        ("Bảo vệ Form (CSRF)", "Flask-WTF 1.3.0 + CSRFProtect", "Tự động sinh và xác thực CSRF Token cho mọi yêu cầu POST/PUT; X-CSRFToken cho AJAX"),
        ("Front-end & UI Styling", "Jinja2, Bootstrap 5.3, Vanilla JS", "Giao diện Glassmorphism hiện đại, responsive đa thiết bị, Fetch API cho giỏ hàng"),
        ("Kiểm thử tự động", "Pytest 9.1.1 (156 Test Cases)", "Kiểm tra tự động toàn diện: CSRF, giỏ hàng, checkout, RBAC 3 vai trò, 7 REST API")
    ]
    add_table(["Thành phần", "Công nghệ sử dụng", "Mô tả vai trò kỹ thuật"], tech_data, [1.5, 2.0, 3.27])

    add_h2("2.2. Kiến trúc Application Factory & Phân hệ Blueprints")
    p_arch = doc.add_paragraph()
    p_arch.add_run(
        "Mã nguồn được phân tách theo mô hình Application Factory với hàm create_app() trong app/__init__.py, "
        "kết nối các thành phần thông qua 4 Blueprints độc lập nằm trực tiếp trong thư mục app/:"
    )

    add_image_with_caption("06_architecture_diagram.png", "Hình 1: Sơ đồ kiến trúc phân tầng hệ thống và 4 Blueprints", width_inches=6.3)

    blueprints = [
        ("app/shop: ", "Giao diện khách hàng: duyệt danh mục, chi tiết sản phẩm, giỏ hàng Session kết hợp Fetch API, thanh toán COD, xem đơn hàng của tôi (/my-orders), gửi đánh giá sản phẩm."),
        ("app/admin: ", "Phân hệ quản trị dành cho Admin và Staff: Dashboard thống kê doanh thu, người dùng và phân loại đơn, quản lý sản phẩm (CRUD dành riêng cho Admin), xem và cập nhật trạng thái đơn hàng."),
        ("app/auth: ", "Phân hệ xác thực: đăng ký tài khoản (/auth/register), đăng nhập (/auth/login) với Flask-Login, đổi mật khẩu an toàn (/auth/change-password), đăng xuất (/auth/logout), chống chuyển hướng độc hại với is_safe_url()."),
        ("app/api: ", "Phân hệ RESTful API: cung cấp 7 endpoints định dạng JSON có xác thực qua Flask-JWT-Extended (Bearer Token), sẵn sàng tích hợp Mobile App hoặc đối tác ngoại vi.")
    ]
    for b_title, b_desc in blueprints:
        p_bp = doc.add_paragraph(style='List Bullet')
        p_bp.paragraph_format.space_after = Pt(2)
        r_bt = p_bp.add_run(b_title)
        r_bt.bold = True
        p_bp.add_run(b_desc)

    add_h2("Ma trận phân quyền RBAC 3 vai trò (Role-Based Access Control)")
    rbac_data = [
        ("Guest (Khách vãng lai)", "Xem danh mục, xem chi tiết sản phẩm, thêm vào giỏ hàng session", "Bị chuyển hướng về trang /auth/login khi thanh toán checkout hoặc truy cập /admin/*"),
        ("Customer (Khách hàng)", "Duyệt shop, giỏ hàng AJAX, checkout đặt hàng, xem lịch sử đơn (/my-orders), viết đánh giá sản phẩm (1 lần/SP)", "Bị chặn 403 Forbidden khi cố tình truy cập bất kỳ endpoint nào thuộc /admin/*"),
        ("Staff (Nhân viên vận hành)", "Đăng nhập admin, xem Dashboard thống kê, xem danh sách/chi tiết đơn hàng, đổi trạng thái đơn (Web & API PUT /orders/<id>/status)", "BỊ CHẶN 403 Forbidden đối với chức năng Quản lý Sản phẩm (Product CRUD: thêm, sửa giá, ẩn sản phẩm)"),
        ("Admin (Quản trị viên)", "Toàn quyền hệ thống: Dashboard thống kê, toàn quyền CRUD Sản phẩm, quản lý và đổi trạng thái đơn hàng, truy cập toàn bộ API", "Không có giới hạn quyền hạn trên hệ thống")
    ]
    add_table(["Vai trò người dùng", "Quyền hạn được cấp phép", "Giới hạn & Ràng buộc an toàn"], rbac_data, [1.6, 2.5, 2.67])

    add_h2("2.3. Thiết kế Cơ sở dữ liệu chuẩn hóa (6 Bảng & Ràng buộc)")
    p_db = doc.add_paragraph()
    p_db.add_run(
        "Cơ sở dữ liệu gồm đúng 6 bảng chuẩn hóa, được quản lý bằng SQLAlchemy ORM và di trú qua 5 revisions Alembic. "
        "Bảng DANHGIA đóng vai trò quan hệ nhiều-nhiều (M:N) thật sự giữa NGUOIDUNG và SANPHAM."
    )

    add_image_with_caption("05_erd_diagram.png", "Hình 2: Sơ đồ thực thể quan hệ cơ sở dữ liệu (ERD) 6 bảng chuẩn hóa", width_inches=6.3)

    db_data = [
        ("NGUOIDUNG", "MANGUOIDUNG (PK, INT)\nHOTEN (NVARCHAR(200))\nEMAIL (VARCHAR(200))\nSDT (VARCHAR(10))\nNGAYSINH (DATE)\nPASSWORD_HASH (VARCHAR(255))\nROLE (VARCHAR(20))\nTRANGTHAIND (INT, def=1)", "Lưu trữ tài khoản với 3 roles: 'admin', 'staff', 'customer'. Mật khẩu băm bằng Werkzeug PBKDF2/scrypt. Email được validate trùng ở tầng form đăng ký. Trạng thái 1: Hoạt động, 0: Khóa."),
        ("DANHMUC", "MADANHMUC (PK, INT)\nTENDM (NVARCHAR(50))", "Lưu 4 danh mục phẳng 1 cấp: Điện thoại (11), Laptop (12), Thời trang nam (21), Thời trang nữ (22). Đã loại bỏ cột MOTA và MADMCHA không dùng."),
        ("SANPHAM", "MASANPHAM (PK, INT)\nTENSPH (NVARCHAR(200))\nHINHANH (VARCHAR(500))\nDONGIA (NUMERIC(18,2))\nMOTA (NVARCHAR(500))\nSOLUONGTON (INT, def=0)\nTRANGTHAISPH (INT, def=1)\nMADANHMUC (FK, INT)", "Lưu 23 sản phẩm thực tế kèm link ảnh. Ràng buộc cấp cơ sở dữ liệu CHECK (SOLUONGTON >= 0) (tên CK_SANPHAM_SOLUONGTON qua migration 4877af4546c5) bảo đảm không bao giờ âm kho. Trạng thái 1: Active, 0: Tạm ẩn."),
        ("DONHANG", "MADONHANG (PK, INT)\nMANGUOIDUNG (FK, INT, NULL)\nNGAYDAT (DATE)\nTONGGIATRI (NUMERIC(18,2))\nTRANGTHAI (INT, def=0)\nHOTENNHAN (NVARCHAR(200))\nDIACHIGIAO (NVARCHAR(300))\nSDTNHAN (VARCHAR(15))", "Quản lý đơn hàng. Khách vãng lai NULL MANGUOIDUNG nếu chưa gắn user. Trạng thái lưu dạng số nguyên 0–3: 0: Mới / Chờ xử lý, 1: Đang xử lý, 2: Hoàn thành, 3: Đã hủy. Cột tổng tiền là TONGGIATRI, số điện thoại là SDTNHAN."),
        ("CHITIETDONHANG", "MADONHANG (PK, FK -> DONHANG)\nMASANPHAM (PK, FK -> SANPHAM)\nSOLUONG (INT)", "Khóa chính ghép kép (MADONHANG, MASANPHAM). Mỗi sản phẩm chỉ xuất hiện 1 lần trong 1 đơn. Không có cột MACHITIET và DONGIA riêng; tổng giá trị đơn được chốt cố định trong TONGGIATRI của đơn hàng."),
        ("DANHGIA", "MADANHGIA (PK, INT)\nMANGUOIDUNG (FK, NOT NULL)\nMASANPHAM (FK, NOT NULL)\nSOSAO (INT, NOT NULL)\nNOIDUNG (NVARCHAR(1000))\nNGAYTAO (DATETIME)", "Quan hệ M:N giữa Người dùng và Sản phẩm. Ràng buộc duy nhất UNIQUE (MANGUOIDUNG, MASANPHAM) (tên UQ_DANHGIA_USER_SP) đảm bảo mỗi user chỉ đánh giá 1 lần/sản phẩm; CHECK (SOSAO BETWEEN 1 AND 5) (tên CK_DANHGIA_SOSAO).")
    ]
    add_table(["Tên Bảng", "Cột chính & Khóa", "Ý nghĩa nghiệp vụ & Ràng buộc"], db_data, [1.4, 2.5, 2.87])

    add_h2("Cơ chế Khóa bi quan (Pessimistic Locking) & Phòng ngự đa tầng")
    p_lock = doc.add_paragraph()
    p_lock.add_run(
        "Để giải quyết triệt để lỗi race condition khi nhiều người dùng cùng lúc bấm thanh toán sản phẩm có số lượng tồn kho còn lại bằng 1, hệ thống triển khai giải pháp phòng thủ hai tầng:\n"
        "• Lớp 1 (Khóa bi quan): Trong app/shop/cart_routes.py:254, truy vấn sản phẩm trước khi trừ tồn kho sử dụng mệnh đề with_for_update():\n"
        "  db.select(SanPham).where(SanPham.MASANPHAM == item['product'].MASANPHAM).with_for_update()\n"
        "  Trên Microsoft SQL Server (Docker / Production), câu lệnh sinh khóa độc quyền UPDLOCK/XLOCK trên dòng dữ liệu trong transaction, buộc các transaction đồng thời khác phải xếp hàng chờ cho đến khi transaction trước commit hoặc rollback.\n"
        "• Lớp 2 (Ràng buộc toàn vẹn Database): Do SQLite (môi trường Local) bỏ qua with_for_update(), hệ thống có lớp phòng vệ thứ hai là ràng buộc cơ sở dữ liệu CHECK (SOLUONGTON >= 0). Nếu phát sinh race condition làm tồn kho âm, Database sẽ chặn ngay lập tức và ném ra ngoại lệ IntegrityError, kích hoạt db.session.rollback() an toàn."
    )

    add_h2("2.4. Danh mục Tính năng cốt lõi & Hệ thống 7 RESTful API")
    p_api = doc.add_paragraph()
    p_api.add_run(
        "Hệ thống cung cấp đầy đủ các tính năng người dùng phía Web và 7 API endpoints chuẩn RESTful xác thực qua JWT Bearer Token:"
    )

    add_image_with_caption("08_api_postman.png", "Hình 3: Kiểm thử hệ thống 7 RESTful API và JWT Bearer Token", width_inches=6.3)

    api_data = [
        ("1", "POST", "/api/auth/token", "Công khai", "Nhận email và password dạng JSON; trả về Bearer JWT token có hạn 30 phút cùng thông tin user (id, name, role). Trả 401 nếu sai mật khẩu hoặc tài khoản bị khóa."),
        ("2", "GET", "/api/health", "Công khai", "Health check kiểm tra trạng thái hoạt động của API server (trả về status: ok, message: API is running)."),
        ("3", "GET", "/api/products", "Công khai", "Danh sách sản phẩm kèm lọc từ khóa (q), lọc danh mục (category), khoảng giá (min_price, max_price), sắp xếp (sort) và phân trang (page, per_page)."),
        ("4", "GET", "/api/products/<int:id>", "Công khai", "Xem chi tiết một sản phẩm theo ID. Trả 404 nếu sản phẩm không tồn tại hoặc ở trạng thái tạm ẩn (TRANGTHAISPH = 0)."),
        ("5", "GET", "/api/orders", "JWT Required", "Xem danh sách đơn hàng có phân trang. Customer chỉ xem được đơn của chính mình; Admin và Staff xem được toàn bộ đơn hàng trong hệ thống."),
        ("6", "GET", "/api/orders/<int:id>", "JWT Required", "Xem chi tiết một đơn hàng gồm thông tin người nhận và danh sách các mặt hàng. Customer bị chặn 403 nếu xem đơn của người khác; Admin/Staff xem được mọi đơn."),
        ("7", "PUT", "/api/orders/<int:id>/status", "Admin/Staff Only", "Cập nhật trạng thái đơn hàng (nhận JSON status: 0-3). Yêu cầu Bearer JWT và quyền Admin hoặc Staff; Customer bị chặn 403 Forbidden.")
    ]
    add_table(["STT", "Method", "Endpoint API", "Xác thực & Quyền", "Mô tả chi tiết chức năng"], api_data, [0.4, 0.7, 2.2, 1.2, 2.27])

    add_callout(
        "LƯU Ý NGHIỆP VỤ ĐẶT HÀNG",
        "API không cung cấp endpoint POST /api/orders. Quy trình đặt hàng được thực hiện độc quyền thông qua giao diện Web tại route /checkout nhằm kiểm soát chặt chẽ giỏ hàng trong session, xác thực form chống CSRF và áp dụng giao dịch khóa bi quan an toàn."
    )

    # ==================== PHẦN 3 ====================
    add_h1("PHẦN 3: GIAO DIỆN NGƯỜI DÙNG & MINH CHỨNG THỰC NGHIỆM")
    p_ui = doc.add_paragraph()
    p_ui.add_run(
        "Giao diện được thiết kế theo phong cách Glassmorphism hiện đại trên nền Bootstrap 5.3, "
        "tương thích hoàn toàn với các kích thước màn hình từ Desktop đến Mobile:"
    )

    add_image_with_caption("01_product_catalog.jpg", "Hình 4: Giao diện Trang chủ & Danh mục sản phẩm (bộ lọc giá, danh mục, phân trang)", width_inches=6.0)
    add_image_with_caption("02_cart_checkout.jpg", "Hình 5: Giao diện Giỏ hàng AJAX tương tác thời gian thực & Thanh toán COD an toàn", width_inches=6.0)
    add_image_with_caption("03_admin_dashboard.jpg", "Hình 6: Giao diện Admin Dashboard (Thống kê doanh thu, phân loại đơn, cảnh báo tồn kho <= 5)", width_inches=6.0)
    add_image_with_caption("04_product_reviews.jpg", "Hình 7: Giao diện Chi tiết sản phẩm & Hệ thống Đánh giá nhận xét (1-5 sao)", width_inches=6.0)

    # ==================== PHẦN 4 ====================
    add_h1("PHẦN 4: HƯỚNG DẪN CÀI ĐẶT & TRIỂN KHAI HỆ THỐNG")

    add_h2("4.1. Cách 1: Chạy trực tiếp với SQLite (Local Testing / Demo nhanh nhất)")
    p_dev = doc.add_paragraph()
    p_dev.add_run("Phương thức này sử dụng SQLite cục bộ có sẵn, cực kỳ thuận tiện cho quá trình kiểm tra và chấm bài:")

    add_code(
        "# Bước 1: Mở terminal tại thư mục dự án và kích hoạt môi trường ảo (Virtualenv)\n"
        ".\\.venv\\Scripts\\activate            # Trên Windows PowerShell / CMD\n"
        "# hoặc: source .venv/bin/activate      # Trên macOS / Linux\n\n"
        "# Bước 2: Cài đặt thư viện phụ thuộc (nếu chưa cài)\n"
        "pip install -r requirements.txt\n\n"
        "# Bước 3: Nạp dữ liệu mẫu 4 danh mục và 23 sản phẩm (nếu chưa nạp)\n"
        "python seed.py\n"
        "python create_test_users.py\n\n"
        "# Bước 4: Khởi động máy chủ phát triển Flask\n"
        "python run.py\n\n"
        "# -> Truy cập trình duyệt web tại: http://127.0.0.1:5000"
    )

    add_h2("4.2. Cách 2: Triển khai Docker Compose & SQL Server 2022 (Port 5050)")
    p_docker = doc.add_paragraph()
    p_docker.add_run(
        "Dành cho môi trường sản xuất chuẩn hóa với cơ sở dữ liệu Microsoft SQL Server 2022 Express. "
        "Yêu cầu thực hiện tuần tự các bước theo đúng hướng dẫn trong README.md:"
    )

    add_code(
        "# Bước 1: Tạo file .env tại thư mục gốc với 3 biến môi trường bắt buộc:\n"
        "SECRET_KEY=your-private-flask-secret-key-12345\n"
        "JWT_SECRET_KEY=your-private-jwt-secret-key-67890\n"
        "MSSQL_SA_PASSWORD=YourStrongPassword!2026\n\n"
        "# Bước 2: Build image ứng dụng Web Flask (chạy non-root user, Gunicorn WSGI):\n"
        "docker compose build web\n\n"
        "# Bước 3: Khởi động container Microsoft SQL Server 2022:\n"
        "docker compose up -d db\n\n"
        "# Bước 4: Khởi tạo database MiniEcommerceDB và nạp schema:\n"
        "docker compose run --rm --no-deps web python -m scripts.bootstrap_db\n\n"
        "# Bước 5: Đánh dấu phiên bản migration hiện tại:\n"
        "docker compose run --rm --no-deps web flask --app run:app db stamp head\n\n"
        "# Bước 6: Khởi chạy container Web:\n"
        "docker compose up -d web\n\n"
        "# -> Truy cập ứng dụng tại địa chỉ: http://localhost:5050 (hoặc http://127.0.0.1:5050)\n"
        "# Để tắt toàn bộ hệ thống khi dừng kiểm tra:\n"
        "docker compose down"
    )

    add_h2("4.3. Bảng tài khoản thử nghiệm có sẵn (Demo Accounts - Đầy đủ 3 Roles)")
    p_acc = doc.add_paragraph()
    p_acc.add_run("Hệ thống khởi tạo sẵn 3 tài khoản thử nghiệm tương ứng 3 vai trò trong ma trận RBAC:")

    account_data = [
        ("Quản trị viên (Admin)", "admin@minishop.local", "Admin@123", "Toàn quyền: Dashboard thống kê, CRUD sản phẩm, duyệt và đổi trạng thái đơn hàng"),
        ("Nhân viên vận hành (Staff)", "staff@minishop.local", "Staff@123", "Vận hành: Dashboard thống kê, xem và đổi trạng thái đơn hàng; Bị chặn 403 ở CRUD sản phẩm"),
        ("Khách hàng (Customer)", "customer@minishop.local", "Customer@123", "Mua sắm: Giỏ hàng, checkout đặt hàng, xem lịch sử đơn cá nhân, gửi đánh giá sản phẩm")
    ]
    add_table(["Vai trò người dùng", "Email đăng nhập", "Mật khẩu", "Quyền hạn & Chức năng thực nghiệm"], account_data, [1.5, 1.8, 1.1, 2.37])

    add_h2("4.4. Bộ kiểm thử tự động Pytest (165 Test Cases Passed)")
    p_test = doc.add_paragraph()
    p_test.add_run(
        "Dự án tích hợp bộ 165 bài kiểm thử tự động với Pytest, chạy hoàn toàn độc lập với database in-memory, "
        "bảo đảm 100% các tiêu chí bảo mật, nghiệp vụ và API đều đạt kết quả PASSED:"
    )

    add_image_with_caption("07_test_terminal.png", "Hình 8: Kết quả chạy thực tế 165/165 bài kiểm thử tự động với Pytest (100% Passed)", width_inches=6.0)

    test_suites_data = [
        ("tests/test_admin.py", "23 tests", "Kiểm tra RBAC 3 vai trò, Dashboard thống kê (doanh thu, người dùng, tồn kho), CRUD sản phẩm, cập nhật đơn"),
        ("tests/test_api_auth.py", "6 tests", "Kiểm tra POST /api/auth/token, Bearer JWT, sai credential, tài khoản bị khóa"),
        ("tests/test_api_orders.py", "14 tests", "Kiểm tra GET /api/orders, GET /api/orders/<id>, PUT /api/orders/<id>/status theo role"),
        ("tests/test_api_products.py", "12 tests", "Kiểm tra GET /api/products, GET /api/products/<id>, lọc danh mục, phân trang"),
        ("tests/test_auth_change_password.py", "8 tests", "Kiểm tra đổi mật khẩu: yêu cầu login, sai pass cũ, pass ngắn, lệch xác nhận, cập nhật hash thành công"),
        ("tests/test_auth_register.py", "9 tests", "Kiểm tra đăng ký, validate form, kiểm tra trùng email, login session, next_url an toàn"),
        ("tests/test_cart_checkout.py", "20 tests", "Kiểm tra thêm/sửa/xóa giỏ hàng AJAX, checkout trừ tồn kho, tính tổng tiền"),
        ("tests/test_csrf_security.py", "9 tests", "Kiểm tra bắt buộc CSRF token trên mọi form POST, chặn request giả mạo"),
        ("tests/test_models.py", "7 tests", "Kiểm tra quan hệ ORM giữa các bảng, Cascade, kiểu dữ liệu Unicode và Numeric"),
        ("tests/test_products.py", "38 tests", "Kiểm tra tìm kiếm từ khóa, sắp xếp giá, phân trang 8 SP/trang, ẩn sản phẩm"),
        ("tests/test_reviews.py", "17 tests", "Kiểm tra đánh giá 1-5 sao, giới hạn 1 đánh giá/user/sp, tính sao trung bình"),
        ("tests/test_stock_constraint.py", "2 tests", "Kiểm tra ràng buộc cấp DB CHECK (SOLUONGTON >= 0) chống bán âm kho")
    ]
    add_table(["Tập tin kiểm thử (Test Suite)", "Số lượng Test", "Nội dung & Mục tiêu kiểm thử"], test_suites_data, [1.8, 1.0, 3.97])

    # ==================== PHẦN 5 ====================
    add_h1("PHẦN 5: PHÂN CÔNG CÔNG VIỆC & QUY TRÌNH PHÁT TRIỂN")

    add_h2("5.1. Bảng phân công trách nhiệm & Tỷ lệ đóng góp")
    members_data = [
        ("Châu Lê Gia Bảo\n(Nhóm trưởng)", "Kiến trúc tổng thể Application Factory, thiết kế Database Models & Migrations, tính năng Shop & Giỏ hàng AJAX (cart.js), tích hợp Docker Compose & SQL Server.", "25%"),
        ("Hà Trung Kiên", "Hệ thống xác thực Flask-Login, Đăng ký/Đăng nhập/Đăng xuất, Đổi mật khẩu (/auth/change-password), Bảo mật CSRFProtect & is_safe_url, Module Đánh giá sản phẩm.", "25%"),
        ("Trần Vũ Hoàng Long", "Phân hệ Quản trị Admin, Ma trận RBAC 3 vai trò (Admin, Staff, Customer), Admin Dashboard thống kê doanh thu & KPI người dùng, CRUD Sản phẩm & Quản lý đơn hàng.", "25%"),
        ("Minh Tuấn", "Xây dựng hệ thống 7 RESTful API JSON, Xác thực Flask-JWT-Extended Bearer Token, Tầng dịch vụ sản phẩm (product_service.py) và bộ lọc tìm kiếm/phân trang.", "25%")
    ]
    add_table(["Thành viên thực hiện", "Nhiệm vụ & Module phụ trách chính", "Đóng góp"], members_data, [1.8, 4.17, 0.8])

    add_h2("5.2. Quy trình làm việc nhóm với Git")
    p_git = doc.add_paragraph()
    p_git.add_run(
        "Nhóm áp dụng mô hình Git Feature Branch Workflow:\n"
        "• Nhánh chính (main): Chỉ chứa mã nguồn ổn định, đã chạy pass toàn bộ 165 test cases và được review kỹ lưỡng.\n"
        "• Nhánh chức năng (feature/*): Từng thành viên tạo nhánh riêng khi phát triển tính năng mới (ví dụ: feature/admin-rbac, feature/jwt-api, feature/change-password, feature/ajax-cart).\n"
        "• Commit Convention: Tuân thủ định dạng chuẩn Conventional Commits (feat: tính năng mới, fix: sửa lỗi, test: viết bài test, refactor: tái cấu trúc code).\n"
        "• Pull Request & Code Review: Mỗi thành viên tạo Pull Request vào main và cần ít nhất một thành viên khác kiểm tra mã nguồn trước khi merge."
    )

    # ==================== PHẦN 6 ====================
    add_h1("PHẦN 6: ĐÁNH GIÁ KẾT QUẢ, HẠN CHẾ & HƯỚNG PHÁT TRIỂN")

    add_h2("6.1. Bảng đối chiếu kết quả thực tế với yêu cầu đề tài")
    eval_data = [
        ("Flask 3.11+, SQL Server", "Đạt yêu cầu", "Python 3.12, Flask 3.1.3; hỗ trợ đồng thời SQLite và SQL Server 2022 qua Docker. pyodbc và ODBC Driver 18.", "SQL Server chạy qua Docker; Local chạy SQLite."),
        (">= 4 bảng, >= 1 quan hệ M:N", "Đạt yêu cầu", "6 bảng chuẩn hóa; DANHGIA là quan hệ M:N giữa User và Sản phẩm có ràng buộc UNIQUE và CHECK sao.", "Tên cột khớp chuẩn xác 100% với model."),
        ("Flask-WTF, CSRF mọi form", "Đạt yêu cầu", "CSRFProtect bật toàn hệ thống; form checkout dùng Flask-WTF; cart.js gửi X-CSRFToken header.", "Một số form admin dùng HTML thuần + CSRF token."),
        ("Flask-Login + RBAC >= 3 role", "Đạt yêu cầu", "Đầy đủ 3 roles: Admin, Staff, Customer; kiểm tra quyền chặt chẽ tại @admin_bp.before_request.", "Staff bị chặn 403 ở CRUD sản phẩm."),
        (">= 3 REST API, JSON, JWT", "Đạt yêu cầu", "7 API endpoints hoàn chỉnh, trả về JSON, xác thực Bearer JWT token, kiểm tra user hoạt động.", "Không có POST đơn qua API; đặt hàng qua web."),
        ("AJAX >= 1 tính năng", "Đạt yêu cầu", "Giỏ hàng tương tác thời gian thực bằng Fetch API (cart.js); cập nhật số lượng và tính tiền không reload.", "Giỏ hàng lưu trữ trong Session."),
        ("Jinja2 + Bootstrap 5", "Đạt yêu cầu", "base.html kế thừa toàn app, Bootstrap 5.3.3, giao diện Glassmorphism hiện đại, responsive mobile.", "Đã bổ sung đầy đủ ảnh chụp minh họa."),
        ("Flask-Migrate / Seed", "Đạt yêu cầu", "5 file migration lịch sử; seed.py nạp 4 danh mục và 23 sản phẩm; create_test_users.py nạp 3 tài khoản demo.", "Hỗ trợ bootstrap tự động trên Docker."),
        ("Docker Containerization", "Đạt yêu cầu", "Dockerfile đa tầng, docker-compose.yml khởi chạy Flask Web (cổng 5050) và SQL Server 2022 Express.", "Chạy bằng user non-root bảo mật."),
        ("Kiểm thử tự động", "Đạt yêu cầu", "165/165 bài kiểm thử tự động với Pytest passed 100% trong 8.55s.", "12 test suites chạy trên SQLite in-memory độc lập.")
    ]
    add_table(["Tiêu chí đề bài", "Trạng thái", "Dẫn chứng kỹ thuật & Minh chứng", "Ghi chú & Giới hạn thực tế"], eval_data, [1.4, 1.0, 2.5, 1.87])

    add_h2("6.2. Các hạn chế hiện tại của hệ thống (Known Limitations)")
    limitations = [
        ("Chưa có tính năng Quên mật khẩu qua Email: ", "Hệ thống đã hiện thực đổi mật khẩu (/auth/change-password) an toàn cho người dùng đã đăng nhập; chức năng gửi token reset mật khẩu qua email khi quên pass chưa được triển khai."),
        ("Màn hình quản trị chưa có chức năng Quản lý người dùng: ", "Admin hiện quản lý Dashboard, Sản phẩm và Đơn hàng; chưa có màn hình giao diện để khóa/mở khóa hoặc đổi role tài khoản người dùng trực tiếp trên Web."),
        ("Giỏ hàng lưu trong Session: ", "Giỏ hàng hiện được lưu trữ trong Flask Session của trình duyệt nên thuận tiện cho cả khách vãng lai, nhưng chưa đồng bộ chéo giữa nhiều thiết bị của cùng một tài khoản."),
        ("Checkout bắt buộc đăng nhập tài khoản: ", "Khi khách bấm tiến hành thanh toán từ giỏ hàng, hệ thống yêu cầu đăng nhập tài khoản để quản lý đơn hàng gắn liền với người mua (chưa hỗ trợ Guest Checkout độc lập)."),
        ("Bảng CHITIETDONHANG chưa lưu đơn giá lịch sử: ", "Chi tiết đơn hàng lưu số lượng và khóa ngoại sản phẩm; tổng tiền đơn được chốt cố định trong TONGGIATRI của bảng DONHANG."),
        ("Chính sách Đánh giá sản phẩm: ", "Hiện tại hệ thống cho phép bất kỳ tài khoản khách hàng nào đã đăng nhập đều có thể viết 1 đánh giá cho mỗi sản phẩm (chưa ràng buộc điều kiện phải có đơn hàng đã hoàn tất sản phẩm đó).")
    ]
    for b_lim, n_lim in limitations:
        p_l = doc.add_paragraph(style='List Bullet')
        p_l.paragraph_format.space_after = Pt(2)
        r_lb = p_l.add_run(b_lim)
        r_lb.bold = True
        r_lb.font.color.rgb = RGBColor(185, 28, 28)
        p_l.add_run(n_lim)

    add_h2("6.3. Hướng phát triển trong tương lai (Future Roadmap)")
    future_work = [
        ("Tích hợp cổng thanh toán trực tuyến: ", "Mở rộng kết nối cổng VNPay, MoMo hoặc ZaloPay để thanh toán qua mã QR bên cạnh phương thức COD truyền thống."),
        ("Ứng dụng di động (Mobile App): ", "Xây dựng ứng dụng di động đa nền tảng bằng React Native hoặc Flutter kết nối trực tiếp với 7 RESTful API JWT đã hoàn thiện."),
        ("Đồng bộ giỏ hàng đa thiết bị: ", "Lưu trữ giỏ hàng trong cơ sở dữ liệu đối với người dùng đã đăng nhập để giỏ hàng không bị mất khi chuyển đổi giữa điện thoại và máy tính."),
        ("Hệ thống gợi ý sản phẩm thông minh: ", "Áp dụng thuật toán Collaborative Filtering để gợi ý các sản phẩm liên quan dựa trên lịch sử xem hàng và đánh giá của khách hàng.")
    ]
    for b_f, n_f in future_work:
        p_f = doc.add_paragraph(style='List Bullet')
        p_f.paragraph_format.space_after = Pt(2)
        r_fb = p_f.add_run(b_f)
        r_fb.bold = True
        r_fb.font.color.rgb = color_primary
        p_f.add_run(n_f)

    # ==================== PHỤ LỤC A ====================
    doc.add_page_break()
    add_h1("PHỤ LỤC A: NHẬT KÝ SỬ DỤNG AI CÓ TRÁCH NHIỆM (AI USAGE LOG)")
    p_ai = doc.add_paragraph()
    p_ai.add_run(
        "Tuân thủ quy chế học thuật của môn học PWD301 và Trường Đại học FPT, nhóm minh bạch toàn bộ quá trình "
        "sử dụng trợ lý lập trình Trí tuệ nhân tạo (Google Gemini / Antigravity IDE) trong suốt các giai đoạn thực hiện dự án:"
    )

    ai_logs = [
        ("1", "15/09/2026", "Châu Lê Gia Bảo", "Gợi ý cấu trúc thư mục Flask Application Factory và chia Blueprints", "Đề xuất cấu trúc module: shop, admin, auth, api, models, services", "Áp dụng cấu trúc thư mục phẳng trong app/"),
        ("2", "22/09/2026", "Châu Lê Gia Bảo", "Tạo các model SQLAlchemy: DanhMuc, SanPham, DonHang, ChiTiet, DanhGia", "Code 6 models với kiểu Unicode, Numeric, quan hệ M:N DanhGia", "Áp dụng 6 model và thêm CK tồn kho >= 0"),
        ("3", "02/10/2026", "Hà Trung Kiên", "Hiện thực Flask-Login, RBAC 3 vai trò, Werkzeug hashing, chống CSRF/Open Redirect", "Đề xuất @admin_required, before_request, is_safe_url, PBKDF2 hash", "Áp dụng vào auth/routes.py, admin/routes.py"),
        ("4", "08/10/2026", "Châu Lê Gia Bảo", "Viết logic giỏ hàng AJAX Fetch API và khóa bi quan with_for_update()", "Code cart.js gửi X-CSRFToken, code with_for_update() khi checkout", "Áp dụng vào cart.js và shop/cart_routes.py"),
        ("5", "14/10/2026", "Trần Vũ Hoàng Long", "Thiết kế Admin Dashboard, thẻ doanh thu, phân loại đơn, CRUD sản phẩm", "Layout Bootstrap 5 dashboard, bảng lọc danh sách, form modal", "Áp dụng vào các template admin và admin/routes.py"),
        ("6", "18/10/2026", "Minh Tuấn", "Xây dựng 7 RESTful API JSON xác thực bằng Flask-JWT-Extended", "Code 7 endpoints: auth/token, health, products, orders", "Áp dụng vào app/api/, kiểm tra user từ DB"),
        ("7", "21/10/2026", "Cả nhóm", "Soạn thảo kịch bản kiểm thử tự động Pytest bao quát CSRF, RBAC, Cart, API", "Cấu trúc fixture SQLite in-memory, viết 156 test cases", "Chạy thực tế đạt 156/156 passed in 6.64s"),
        ("8", "23/10/2026", "Châu Lê Gia Bảo", "Cấu hình Dockerfile đa tầng và docker-compose.yml chạy SQL Server 2022", "Dockerfile ODBC 18, gunicorn non-root; docker-compose cổng 5050", "Áp dụng vào Dockerfile, docker-compose.yml"),
        ("9", "24/10/2026", "Cả nhóm", "Đối chiếu báo cáo với mã nguồn thực tế theo phản hồi của người chấm thi", "Phát hiện sai sót Bcrypt/Werkzeug, sai endpoint, sai cột DB", "Cập nhật tài liệu docs/ và sinh lại báo cáo Word"),
        ("10", "24/10/2026", "Cả nhóm", "Hoàn thiện mã nguồn: bổ sung Đổi mật khẩu (/auth/change-password) và KPI Tổng người dùng", "Code view change_password, template change_password.html, user_count trong dashboard, 9 unit tests", "Áp dụng vào app/auth/routes.py, admin/routes.py, tests/ (165 test cases passed)")
    ]
    add_table(["STT", "Ngày", "Thành viên", "Mục tiêu & Tóm tắt Prompt", "Đề xuất của AI", "Phần áp dụng thực tế vào repo"], ai_logs, [0.4, 0.8, 1.2, 1.7, 1.5, 1.17])

    # ==================== PHỤ LỤC B ====================
    add_h1("PHỤ LỤC B: TÀI LIỆU THAM KHẢO & QUY CHUẨN KỸ THUẬT")
    refs = [
        ("Flask Documentation (v3.1.x): ", "https://flask.palletsprojects.com/ — Application Factory, Blueprints, Sessions, and Signals."),
        ("SQLAlchemy 2.0 Documentation: ", "https://docs.sqlalchemy.org/ — ORM Mappings, Relationships, and with_for_update() Locking."),
        ("Flask-Login Documentation: ", "https://flask-login.readthedocs.io/ — User authentication, session management, and UserMixin."),
        ("Flask-JWT-Extended Documentation: ", "https://flask-jwt-extended.readthedocs.io/ — Protecting views with JSON Web Tokens."),
        ("OWASP Top 10 Web Application Security Risks: ", "https://owasp.org/www-project-top-ten/ — CSRF, XSS, and Secure Authentication."),
        ("Microsoft Learn - SQL Server 2022 & ODBC Driver 18: ", "https://learn.microsoft.com/en-us/sql/connect/odbc/linux/ — Docker Deployment."),
        ("Bootstrap 5.3 Documentation: ", "https://getbootstrap.com/docs/5.3/ — Responsive Grid, Modals, Forms, and Utility Classes.")
    ]
    for r_title, r_url in refs:
        p_r = doc.add_paragraph(style='List Bullet')
        p_r.paragraph_format.space_after = Pt(2)
        r_rt = p_r.add_run(r_title)
        r_rt.bold = True
        r_rt.font.color.rgb = color_primary
        p_r.add_run(r_url)

    add_callout(
        "KẾT LUẬN & CAM KẾT HỌC THUẬT",
        "Báo cáo đồ án Topic 8 (Mini E-Commerce Store) phản ánh trung thực 100% kiến trúc, mã nguồn thực tế và kết quả kiểm nghiệm của nhóm tại kho lưu trữ GitHub ChauLeGiaBao/MiniEcommerce-PWD301. Toàn bộ các khiếm khuyết được chỉ ra đã được rà soát, đính chính và bổ sung đầy đủ minh chứng thực nghiệm."
    )

    # Lưu file Word
    output_path = os.path.join(BASE_DIR, "Bao_Cao_De_Tai_Topic_8_MiniEcommerce.docx")
    try:
        doc.save(output_path)
        print(f"[SUCCESS] Comprehensive project report generated successfully at: {output_path}")
    except PermissionError:
        fallback_path = os.path.join(BASE_DIR, "Bao_Cao_De_Tai_Topic_8_MiniEcommerce_CapNhat.docx")
        doc.save(fallback_path)
        print(f"[WARN] File dang mo trong Microsoft Word. Da luu ban cap nhat moi nhat vao: {fallback_path}")

if __name__ == "__main__":
    build_comprehensive_document()
