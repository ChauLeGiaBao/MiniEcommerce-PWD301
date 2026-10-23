# -*- coding: utf-8 -*-
"""
Script tạo tài liệu báo cáo đồ án Word (.docx) chuyên nghiệp cho đề tài:
Topic 8: Mini E-Commerce Store - Môn học PWD301.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Đặt màu nền cho cell trong bảng."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt lề trong (padding) cho cell (đơn vị dxa: 20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    """Đặt đường viền tinh tế cho bảng."""
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

def build_document():
    doc = docx.Document()

    # 1. Page Setup (A4, 1 inch margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # Styles
    primary_color = RGBColor(26, 54, 93)     # Deep Navy #1A365D
    secondary_color = RGBColor(43, 108, 176) # Blue #2B6CB0
    dark_neutral = RGBColor(45, 55, 72)      # Charcoal #2D3748
    gray_subtext = RGBColor(113, 128, 150)   # Slate Gray #718096

    # Normal Style configuration
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = dark_neutral
    style_normal.paragraph_format.line_spacing = 1.2
    style_normal.paragraph_format.space_after = Pt(6)

    # --- COVER PAGE ---
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst1 = p_inst.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO - TRƯỜNG ĐẠI HỌC FPT\n")
    r_inst1.bold = True
    r_inst1.font.size = Pt(12)
    r_inst1.font.color.rgb = primary_color
    r_inst2 = p_inst.add_run("KHOA CÔNG NGHỆ THÔNG TIN - BỘ MÔN KỸ THUẬT PHẦN MỀM\n")
    r_inst2.bold = True
    r_inst2.font.size = Pt(11)
    r_inst2.font.color.rgb = gray_subtext

    doc.add_paragraph("\n" * 2)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run("BÁO CÁO ĐỒ ÁN MÔN HỌC: PWD301\n(Web Application Development with Python)\n\n")
    r_sub.font.size = Pt(13)
    r_sub.bold = True
    r_sub.font.color.rgb = secondary_color

    r_main_title = p_title.add_run("ĐỀ TÀI: TOPIC 8\nMINI E-COMMERCE STORE\n")
    r_main_title.font.size = Pt(22)
    r_main_title.bold = True
    r_main_title.font.color.rgb = primary_color

    r_vi_title = p_title.add_run("XÂY DỰNG HỆ THỐNG CỬA HÀNG TRỰC TUYẾN THU NHỎ HOÀN CHỈNH VỚI PYTHON FLASK VÀ MICROSOFT SQL SERVER")
    r_vi_title.font.size = Pt(12)
    r_vi_title.italic = True
    r_vi_title.font.color.rgb = dark_neutral

    doc.add_paragraph("\n" * 3)

    # Group Info Box
    tbl_info = doc.add_table(rows=6, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_info.autofit = False

    info_data = [
        ("Mã môn học / Lớp:", "PWD301 - Lập trình ứng dụng Web với Python (Python Web Development)"),
        ("Đề tài chỉ định:", "Topic 8: Mini E-Commerce Store"),
        ("Giảng viên hướng dẫn:", "Giảng viên bộ môn Kỹ thuật Phần mềm (SE) - FPT University"),
        ("Nhóm sinh viên thực hiện:", "Châu Lê Gia Bảo (Nhóm trưởng)\nHà Trung Kiên\nTrần Vũ Hoàng Long\nMinh Tuấn"),
        ("Nền tảng công nghệ:", "Flask 3.x, Python 3.12+, SQL Server 2022, Docker, Flask-Login, Flask-WTF, JWT"),
        ("Thời gian thực hiện:", "Học kỳ 5 (Năm học 2025 - 2026)")
    ]

    for idx, (label, val) in enumerate(info_data):
        row = tbl_info.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.3)
        
        p_l = cell_lbl.paragraphs[0]
        r_l = p_l.add_run(label)
        r_l.bold = True
        r_l.font.color.rgb = primary_color
        
        p_v = cell_val.paragraphs[0]
        r_v = p_v.add_run(val)
        r_v.font.color.rgb = dark_neutral
        
        set_cell_background(cell_lbl, "F7FAFC")
        set_cell_background(cell_val, "F7FAFC")
        set_cell_margins(cell_lbl, top=80, bottom=80, left=100, right=100)
        set_cell_margins(cell_val, top=80, bottom=80, left=100, right=100)

    set_table_borders(tbl_info, color="CBD5E0", sz="4")

    doc.add_page_break()

    # --- HELPER FUNCTIONS FOR SECTIONS ---
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(16)
        r.bold = True
        r.font.color.rgb = primary_color
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(13)
        r.bold = True
        r.font.color.rgb = secondary_color
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = dark_neutral
        return p

    def add_callout(text, title="LƯU Ý QUAN TRỌNG:"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.rows[0].cells[0]
        cell.width = Inches(6.5)
        set_cell_background(cell, "EBF8FF")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        
        # Border left thick blue
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="2B6CB0"/>'
            f'  <w:top w:val="none"/>'
            f'  <w:bottom w:val="none"/>'
            f'  <w:right w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(0)
        r_title = p.add_run(title + " ")
        r_title.bold = True
        r_title.font.color.rgb = secondary_color
        r_text = p.add_run(text)
        r_text.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_code(text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.rows[0].cells[0]
        cell.width = Inches(6.5)
        set_cell_background(cell, "F7FAFC")
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
            f'  <w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(45, 55, 72)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_custom_table(headers, rows_data, col_widths=None):
        table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Header Row
        header_row = table.rows[0]
        for col_idx, header_text in enumerate(headers):
            cell = header_row.cells[col_idx]
            if col_widths and col_idx < len(col_widths):
                cell.width = Inches(col_widths[col_idx])
            set_cell_background(cell, "1A365D")
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(header_text)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            r.font.size = Pt(10)

        # Data Rows
        for r_idx, row_values in enumerate(rows_data):
            row = table.rows[r_idx + 1]
            bg_color = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, cell_value in enumerate(row_values):
                cell = row.cells[c_idx]
                if col_widths and c_idx < len(col_widths):
                    cell.width = Inches(col_widths[c_idx])
                set_cell_background(cell, bg_color)
                set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                r = p.add_run(str(cell_value))
                r.font.size = Pt(9.5)

        set_table_borders(table, color="CBD5E0", sz="4")
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        return table

    # --- TABLE OF CONTENTS SUMMARY ---
    add_h1("MỤC LỤC TỔNG QUAN BÁO CÁO")
    toc_p = doc.add_paragraph()
    toc_p.paragraph_format.line_spacing = 1.3
    toc_items = [
        ("PHẦN I: MỤC TIÊU ĐỀ TÀI (PROJECT OBJECTIVES & SCOPE)", 
         "Bối cảnh, mục tiêu tổng quan, chi tiết 12 yêu cầu chung môn học PWD301, phạm vi nghiệp vụ Topic 8."),
        ("PHẦN II: THÀNH PHẦN ĐỀ TÀI & THIẾT KẾ KIẾN TRÚC (SYSTEM ARCHITECTURE & COMPONENTS)", 
         "Ngăn xếp công nghệ, kiến trúc Application Factory, thiết kế CSDL 6 bảng, quan hệ M:N DANHGIA, ma trận phân quyền RBAC 3 vai trò, đặc tả 7 REST API JWT, tính năng AJAX realtime, chống race-condition."),
        ("PHẦN III: HƯỚNG DẪN CÀI ĐẶT & VẬN HÀNH (EXECUTION & DEPLOYMENT GUIDE)", 
         "Cài đặt chạy Local với SQLite, triển khai Production chuẩn Docker + Microsoft SQL Server 2022, chạy bộ kiểm thử tự động pytest (144/144 passed), thông tin tài khoản demo."),
        ("PHẦN IV: TỔNG KẾT & ĐÁNH GIÁ ĐỀ TÀI (CONCLUSION & EVALUATION)", 
         "Bảng đối chiếu 12/12 tiêu chí chấm điểm PWD301, bảng phân công nhiệm vụ và đóng góp của các thành viên, nhật ký ứng dụng AI (AI Usage Log), ưu điểm, hạn chế và hướng phát triển.")
    ]
    for title, desc in toc_items:
        p_item = doc.add_paragraph()
        r_t = p_item.add_run(f"• {title}\n")
        r_t.bold = True
        r_t.font.color.rgb = primary_color
        r_d = p_item.add_run(f"  Tóm tắt: {desc}")
        r_d.italic = True
        r_d.font.color.rgb = gray_subtext

    doc.add_page_break()

    # =========================================================================
    # PHẦN I: MỤC TIÊU ĐỀ TÀI
    # =========================================================================
    add_h1("PHẦN I: MỤC TIÊU ĐỀ TÀI (PROJECT OBJECTIVES & SCOPE)")

    add_h2("1.1. Bối cảnh và Lý do lựa chọn đề tài")
    doc.add_paragraph(
        "Trong bối cảnh nền kinh tế số và thương mại điện tử (E-Commerce) bùng nổ, việc xây dựng các nền tảng bán hàng trực "
        "tuyến có hiệu năng cao, bảo mật vững chắc và trải nghiệm mượt mà là một nhu cầu thiết yếu đối với mọi doanh nghiệp. "
        "Đề tài Topic 8: Mini E-Commerce Store trong môn học PWD301 (Phát triển ứng dụng Web với Python) đặt ra bài toán mô phỏng "
        "toàn diện quy trình mua sắm và quản lý bán hàng (End-to-End Purchase & Order Management Flow), đòi hỏi sinh viên phải "
        "kết hợp nhuần nhuyễn giữa kiến trúc Backend hiện đại với Python Flask, hệ quản trị cơ sở dữ liệu doanh nghiệp Microsoft SQL Server, "
        "và giao diện người dùng tương tác động không tải lại trang (AJAX/Fetch API)."
    )

    add_h2("1.2. Mục tiêu tổng quan của dự án")
    doc.add_paragraph(
        "Mục tiêu cốt lõi của đề tài là xây dựng một hệ thống website thương mại điện tử thu nhỏ nhưng đạt chuẩn công nghiệp, "
        "hoàn chỉnh từ khâu tiếp cận sản phẩm của khách hàng cho đến quy trình vận hành và kiểm soát của đội ngũ quản trị viên:\n"
        "1. Trải nghiệm người dùng thông suốt: Cung cấp danh mục sản phẩm trực quan, tính năng tìm kiếm đa tiêu chí, bộ lọc giá thông minh, "
        "trang chi tiết sản phẩm kèm hệ thống đánh giá/bình luận đa chiều (Reviews).\n"
        "2. Tương tác giỏ hàng thời gian thực: Giỏ hàng lưu trữ theo phiên làm việc (Session-based Cart) kết hợp AJAX/Fetch API giúp "
        "khách hàng thêm sản phẩm, cập nhật số lượng và xóa mặt hàng tức thời mà không cần reload trang.\n"
        "3. Thanh toán và xử lý đơn hàng tin cậy: Quy trình Checkout chặt chẽ với xác thực biểu mẫu phía máy chủ (Server-side Validation), "
        "bảo vệ giao dịch dữ liệu theo tính chất nguyên tử (Atomic Database Transaction), ngăn chặn hoàn toàn nguy cơ bán âm hàng tồn kho (Race Condition / Over-selling).\n"
        "4. Quản trị và phân tích điều hành: Cung cấp trung tâm quản trị (Admin Dashboard) hiển thị các chỉ số kinh doanh then chốt (doanh thu thực tế, "
        "tổng đơn theo trạng thái, cảnh báo sản phẩm sắp hết hàng), quản lý sản phẩm (CRUD) và xử lý luồng trạng thái đơn hàng."
    )

    add_h2("1.3. Mục tiêu kỹ thuật & Đối chiếu 12 Tiêu chuẩn chung môn học PWD301")
    doc.add_paragraph(
        "Dự án được thiết kế bám sát và hiện thực hóa đầy đủ 12 yêu cầu kỹ thuật nền tảng (General Requirements for all topics) "
        "theo đề cương môn học PWD301 của Đại học FPT:"
    )

    gen_reqs = [
        ("Yêu cầu 1", "Framework Flask (Python 3.11+)", "Sử dụng Python 3.12+ và Flask 3.1.3 theo kiến trúc Application Factory hiện đại."),
        ("Yêu cầu 2", "SQL Server & SQLAlchemy ORM", "Sử dụng Microsoft SQL Server 2022 làm CSDL chính thức, ORM với 6 bảng và quan hệ Nhiều-Nhiều qua bảng DANHGIA."),
        ("Yêu cầu 3", "Flask-WTF Forms & CSRF", "Bảo vệ CSRF toàn cục, xác thực nghiêm ngặt phía server trên toàn bộ các biểu mẫu (Checkout, Login, Admin Product)."),
        ("Yêu cầu 4", "Flask-Login & RBAC (>= 3 Roles)", "Triển khai phân quyền theo vai trò chặt chẽ với 3 vai trò: Admin, Staff, Customer (+ đối tượng Guest)."),
        ("Yêu cầu 5", "REST API (>= 3 Endpoints) & JWT", "Xây dựng 7 endpoints RESTful chuẩn JSON, bảo mật truy cập bằng JWT (Flask-JWT-Extended)."),
        ("Yêu cầu 6", "AJAX / Fetch API (No reload)", "Tương tác giỏ hàng thời gian thực (thêm, cập nhật số lượng debounce, xóa, tính tổng tiền tức thời)."),
        ("Yêu cầu 7", "Jinja2 Inheritance & Bootstrap 5", "Cấu trúc template kế thừa từ base.html, giao diện thiết kế responsive, hiện đại trên Bootstrap 5."),
        ("Yêu cầu 8", "Database Migration & Seed Data", "Quản lý tiến hóa schema bằng Flask-Migrate (Alembic), cung cấp file seed.py nạp sẵn dữ liệu phong phú."),
        ("Yêu cầu 9", "Containerization với Docker", "Đóng gói toàn diện hệ thống gồm 2 containers: Web (Gunicorn) và Database (MS SQL Server 2022) qua Docker Compose."),
        ("Yêu cầu 10", "AI Tools & AI Usage Log", "Ứng dụng GitHub Copilot và Google Antigravity trong thiết kế kiến trúc, sinh test cases và lưu vết nhật ký chi tiết."),
        ("Yêu cầu 11", "Quản lý mã nguồn trên Git & README", "Quản lý mã nguồn theo Git chuẩn, quy chuẩn commit rõ ràng, README.md tài liệu hóa chi tiết cách cài đặt."),
        ("Yêu cầu 12", "Kiểm thử tự động & Báo cáo", "Hệ thống kiểm thử tự động với Pytest đạt 144/144 test cases passed 100%, sẵn sàng cho demo và bảo vệ.")
    ]
    add_custom_table(["Tiêu chuẩn PWD301", "Nội dung quy định", "Mức độ đáp ứng trong dự án"], gen_reqs, [1.3, 2.0, 3.2])

    add_h2("1.4. Phạm vi đề tài (Project Scope)")
    doc.add_paragraph(
        "Theo định hướng của Topic 8, dự án tập trung chuyên sâu vào chu trình mua bán và quản trị nội bộ khép kín (End-to-end Purchase Flow). "
        "Dự án không tích hợp cổng thanh toán trực tuyến của bên thứ ba (như VNPay, Momo hay Stripe), mà mô phỏng phương thức giao hàng thu tiền tận nơi "
        "(COD - Cash on Delivery). Điều này giúp toàn bộ nỗ lực kỹ thuật tập trung vào việc chuẩn hóa mô hình dữ liệu, tối ưu hóa giao dịch nguyên tử "
        "khi checkout, kiểm soát tồn kho chống xung đột và phân quyền RBAC đa tầng."
    )

    doc.add_page_break()

    # =========================================================================
    # PHẦN II: THÀNH PHẦN ĐỀ TÀI & THIẾT KẾ KIẾN TRÚC
    # =========================================================================
    add_h1("PHẦN II: THÀNH PHẦN ĐỀ TÀI & THIẾT KẾ KIẾN TRÚC")

    add_h2("2.1. Ngăn xếp công nghệ tổng thể (Technology Stack Matrix)")
    doc.add_paragraph(
        "Dự án được xây dựng dựa trên sự kết hợp hài hòa của các công nghệ phần mềm vững chắc, ổn định và tuân thủ các nguyên tắc thiết kế sạch (Clean Architecture):"
    )

    tech_stack_data = [
        ("Backend Framework", "Python 3.12, Flask 3.1.3", "Nền tảng phát triển web chính, mô hình Application Factory modular."),
        ("Database & ORM", "Microsoft SQL Server 2022, SQLAlchemy 2.0, pyodbc", "CSDL quan hệ doanh nghiệp mạnh mẽ; ORM thao tác dữ liệu an toàn chống SQL Injection."),
        ("Database Migrations", "Flask-Migrate 4.1.0, Alembic 1.19.2", "Quản lý lịch sử thay đổi cấu trúc bảng CSDL đồng bộ giữa mã nguồn và database."),
        ("Authentication", "Flask-Login 0.6.3, Flask-JWT-Extended 4.7.1", "Quản lý phiên đăng nhập trên giao diện web và cấp phát token JWT cho các REST API."),
        ("Forms & Security", "Flask-WTF 1.3.0, WTForms 3.2.2, Werkzeug", "Bảo vệ CSRF Token toàn cục, băm mật khẩu PBKDF2/SHA256, kiểm tra tính hợp lệ dữ liệu."),
        ("Frontend & UI", "HTML5, CSS3, Bootstrap 5.3, JavaScript (Fetch API)", "Giao diện hiện đại, responsive thích ứng trên di động, máy tính bảng và màn hình lớn."),
        ("DevOps & Server", "Docker, Docker Compose, Gunicorn (WSGI Server)", "Đóng gói container độc lập, triển khai sản xuất với máy chủ WSGI nhiều worker threads."),
        ("Testing Framework", "Pytest 9.1.1", "Bộ kiểm thử tự động toàn diện kiểm tra models, routes, API, CSRF, giỏ hàng và thanh toán.")
    ]
    add_custom_table(["Thành phần", "Công nghệ / Thư viện", "Mô tả vai trò trong kiến trúc"], tech_stack_data, [1.5, 2.2, 2.8])

    add_h2("2.2. Kiến trúc Ứng dụng & Cấu trúc Thư mục (Application Architecture)")
    doc.add_paragraph(
        "Hệ thống áp dụng mẫu thiết kế Application Factory Pattern kết hợp phân chia Blueprints theo các miền nghiệp vụ độc lập "
        "(Domain-Driven Segregation). Điểm vào của ứng dụng là hàm create_app() trong app/__init__.py, nơi khởi tạo cấu hình, "
        "kết nối các tiện ích mở rộng (db, migrate, login_manager, jwt, csrf) và đăng ký các Blueprints chức năng:"
    )

    blueprints_info = [
        ("shop_bp (/)", "Shop & Customer Blueprint", "Xử lý duyệt sản phẩm, tìm kiếm, lọc giá, chi tiết sản phẩm, đánh giá (Reviews), giỏ hàng AJAX, checkout và lịch sử đơn cá nhân (My Orders)."),
        ("admin_bp (/admin)", "Admin & Operations Blueprint", "Quản trị viên và nhân viên vận hành: Dashboard thống kê doanh thu/tồn kho, CRUD sản phẩm, quản lý duyệt và đổi trạng thái đơn hàng."),
        ("auth_bp (/auth)", "Authentication Blueprint", "Xử lý đăng ký tài khoản khách hàng, đăng nhập hệ thống, đăng xuất và điều hướng người dùng tự động theo phân quyền vai trò (Role-based redirect)."),
        ("api_bp (/api)", "RESTful API Service", "Cung cấp các endpoints chuẩn hóa phục vụ tích hợp bên ngoài: kiểm tra sức khỏe hệ thống, lấy danh mục sản phẩm, đăng nhập cấp token JWT, quản lý đơn hàng.")
    ]
    add_custom_table(["Blueprint", "Tên miền chức năng", "Nhiệm vụ nghiệp vụ đảm nhiệm"], blueprints_info, [1.3, 1.8, 3.4])

    doc.add_paragraph("Cấu trúc cây thư mục của toàn bộ dự án:")
    add_code(
        "MiniEcommerce-PWD301/\n"
        "├── app/\n"
        "│   ├── __init__.py            # Application Factory: khởi tạo app, cấu hình extensions & Blueprints\n"
        "│   ├── extensions.py          # Khởi tạo db, migrate, login_manager, jwt, csrf độc lập\n"
        "│   ├── admin/                 # Phân hệ Quản trị (Admin routes, forms, decorators)\n"
        "│   ├── api/                   # Phân hệ REST API (auth_routes, order_routes, routes)\n"
        "│   ├── auth/                  # Phân hệ Xác thực (Login, Register, Logout routes, forms)\n"
        "│   ├── models/                # Lớp thực thể SQLAlchemy (6 bảng: DanhMuc, SanPham, User,...)\n"
        "│   ├── services/              # Lớp nghiệp vụ logic (product_service, review_service)\n"
        "│   ├── shop/                  # Phân hệ Cửa hàng (product_routes, cart_routes, forms)\n"
        "│   ├── static/                # Tài nguyên tĩnh: CSS tùy biến, JS (cart.js, admin.js), Images\n"
        "│   └── templates/             # Giao diện Jinja2 kế thừa base.html (products, cart, admin,...)\n"
        "├── migrations/                # Lịch sử các phiên bản migration CSDL của Alembic\n"
        "├── scripts/                   # Scripts hỗ trợ: bootstrap_db.py, migrate_sqlite_to_mssql.py\n"
        "├── tests/                     # 144 kiểm thử tự động pytest (test_admin, test_cart, test_api,...)\n"
        "├── config.py                  # Lớp cấu hình nạp từ biến môi trường .env\n"
        "├── Dockerfile                 # Đóng gói image web Flask chạy Gunicorn trên Debian bookworm\n"
        "├── docker-compose.yml         # Khởi tạo 2 services: web và db (MS SQL Server 2022)\n"
        "├── seed.py                    # Script nạp CSDL và dữ liệu sản phẩm/danh mục mẫu chuẩn\n"
        "├── create_test_users.py       # Script khởi tạo các tài khoản demo (Admin, Staff, Customer)\n"
        "└── requirements.txt           # Danh mục các thư viện phụ thuộc của dự án"
    )

    add_h2("2.3. Thiết kế Cơ sở Dữ liệu (Database Schema, Relationships & Migrations)")
    doc.add_paragraph(
        "Cơ sở dữ liệu được thiết kế chặt chẽ theo dạng chuẩn 3NF (Third Normal Form) trên Microsoft SQL Server. "
        "Mô hình dữ liệu bao gồm 6 bảng thực thể, hoàn toàn đáp ứng và vượt mức tiêu chuẩn tối thiểu (quy định tối thiểu 4 bảng và 1 quan hệ Nhiều-Nhiều):"
    )

    schema_tables = [
        ("DANHMUC", "DanhMuc", "Chứa thông tin danh mục hàng hóa (Điện thoại, Laptop, Thời trang...).", "MADANHMUC (PK), TENDM"),
        ("SANPHAM", "SanPham", "Chứa thông tin sản phẩm, đơn giá, tồn kho, mô tả và trạng thái mở bán.", "MASANPHAM (PK), TENSPH, HINHANH, DONGIA, MOTA, SOLUONGTON, TRANGTHAISPH, MADANHMUC (FK)"),
        ("NGUOIDUNG", "User", "Lưu trữ tài khoản người dùng, mật khẩu băm, vai trò và trạng thái kích hoạt.", "MANGUOIDUNG (PK), HOTEN, EMAIL, SDT, NGAYSINH, PASSWORD_HASH, ROLE, TRANGTHAIND"),
        ("DONHANG", "DonHang", "Lưu trữ thông tin đơn đặt hàng, tổng tiền, ngày đặt, thông tin giao hàng.", "MADONHANG (PK), MANGUOIDUNG (FK, NULL nếu là khách vãng lai), NGAYDAT, TONGGIATRI, TRANGTHAI, HOTENNHAN, DIACHIGIAO, SDTNHAN"),
        ("CHITIETDONHANG", "ChiTietDonHang", "Chi tiết mặt hàng trong đơn; Khóa chính phức hợp ghép giữa đơn và sản phẩm.", "MADONHANG (PK, FK), MASANPHAM (PK, FK), SOLUONG"),
        ("DANHGIA", "DanhGia", "Bảng liên kết quan hệ Nhiều - Nhiều (M:N) giữa User và Product kèm số sao & nhận xét.", "MADANHGIA (PK), MANGUOIDUNG (FK), MASANPHAM (FK), SOSAO, NOIDUNG, NGAYTAO")
    ]
    add_custom_table(["Tên bảng CSDL", "Model Class", "Ý nghĩa nghiệp vụ", "Các trường thông tin cốt lõi"], schema_tables, [1.3, 1.1, 2.3, 1.8])

    add_callout(
        "Quan hệ Nhiều - Nhiều (M:N) giữa NGUOIDUNG và SANPHAM được thiết lập thông qua bảng DANHGIA: một người dùng có thể "
        "đánh giá nhiều sản phẩm khác nhau, và một sản phẩm có thể nhận được đánh giá từ nhiều người dùng. "
        "Bảng có ràng buộc duy nhất UQ_DANHGIA_USER_SP (chặn spam, mỗi người chỉ đánh giá 1 lần trên 1 sản phẩm) "
        "và ràng buộc kiểm tra CK_DANHGIA_SOSAO (chỉ cho phép số sao từ 1 đến 5).",
        title="ĐÁP ỨNG TIÊU CHUẨN QUAN HỆ NHIỀU - NHIỀU (M:N):"
    )

    doc.add_paragraph("Các ràng buộc toàn vẹn dữ liệu (Data Integrity Constraints) được kiểm soát nghiêm ngặt:")
    doc.add_paragraph(
        "• Ràng buộc tồn kho không âm (CK_SANPHAM_SOLUONGTON): Ngăn chặn tuyệt đối việc số lượng tồn kho bị giảm xuống dưới 0 khi xảy ra lỗi đồng thời.\n"
        "• Ràng buộc trạng thái bán hàng: Sản phẩm có TRANGTHAISPH = 1 mới hiển thị trên giao diện cửa hàng và cho phép thêm vào giỏ. Sản phẩm TRANGTHAISPH = 0 được bảo vệ chỉ cho phép quản trị viên xem.\n"
        "• Ràng buộc trạng thái đơn hàng (VALID_ORDER_STATUSES): Quản lý vòng đời đơn theo các hằng số: 0 (Mới / Chờ xử lý), 1 (Đang xử lý), 2 (Hoàn thành), 3 (Đã hủy).\n"
        "• Tiến hóa CSDL an toàn qua Flask-Migrate: Toàn bộ quá trình thay đổi schema được theo dõi qua 5 revisions Alembic: f14dcd86bf53 (mở rộng ảnh) -> b2a434abe7a9 (thêm thông tin nhận hàng) -> c562dfbd1758 (chuẩn hóa kiểu tiền Numeric và SĐT) -> b9953ac12c5e (thêm bảng DANHGIA M:N) -> 4877af4546c5 (thêm CHECK tồn kho không âm)."
    )

    add_h2("2.4. Phân quyền Người dùng & Ma trận RBAC (Role-Based Access Control)")
    doc.add_paragraph(
        "Hệ thống hiện thực hóa phân quyền truy cập theo vai trò (RBAC) với 3 vai trò tài khoản chính thức (Admin, Staff, Customer) "
        "cùng đối tượng khách vãng lai (Guest). Việc kiểm tra quyền được thực thi ở tầng middleware (before_request hook) và các decorators "
        "tùy biến (@admin_required, @login_required), đối chiếu trực tiếp dữ liệu vai trò từ database, tuyệt đối không tin cậy dữ liệu session client:"
    )

    rbac_matrix = [
        ("Duyệt xem sản phẩm, tìm kiếm, lọc giá", "Cho phép", "Cho phép", "Cho phép", "Cho phép"),
        ("Thêm giỏ hàng, cập nhật giỏ hàng (AJAX)", "Cho phép", "Cho phép", "Cho phép", "Cho phép"),
        ("Đặt hàng Checkout (COD)", "Cho phép", "Cho phép", "Cho phép", "Cho phép"),
        ("Xem chi tiết đơn hàng vừa đặt qua session", "Cho phép", "Cho phép", "Cho phép", "Cho phép"),
        ("Đăng nhập, đăng ký tài khoản mới", "Không cần", "Đã đăng nhập", "Đã đăng nhập", "Đã đăng nhập"),
        ("Gửi đánh giá, bình luận sản phẩm (Review)", "Bị chặn (Yêu cầu login)", "Cho phép", "Cho phép", "Cho phép"),
        ("Xem lịch sử đơn hàng cá nhân (/my-orders)", "Bị chặn (401/Login)", "Xem đơn của mình", "Xem đơn của mình", "Xem đơn của mình"),
        ("Truy cập Admin Dashboard (/admin)", "Bị chặn (401/Login)", "Bị chặn (403 Forbidden)", "Cho phép", "Cho phép"),
        ("Quản lý danh sách & duyệt đơn hàng", "Bị chặn", "Bị chặn", "Cho phép (Xem & đổi trạng thái)", "Toàn quyền quản lý"),
        ("Quản lý Sản phẩm (Thêm/Sửa/Xóa/Ẩn sản phẩm)", "Bị chặn", "Bị chặn", "Bị chặn (403 Forbidden)", "Toàn quyền CRUD"),
        ("Gọi REST API đơn hàng (/api/orders)", "Bị chặn (Yêu cầu JWT)", "Xem đơn của mình", "Xem toàn bộ đơn", "Xem toàn bộ đơn"),
        ("Đổi trạng thái đơn qua API (/api/orders/<id>/status)", "Bị chặn", "Bị chặn", "Cho phép", "Cho phép")
    ]
    add_custom_table(["Hành động / Quyền hạn trên hệ thống", "Khách (Guest)", "Khách hàng (Customer)", "Nhân viên (Staff)", "Quản trị viên (Admin)"], rbac_matrix, [2.3, 1.0, 1.1, 1.1, 1.0])

    add_h2("2.5. Chi tiết các Phân hệ Chức năng (Functional Modules)")
    doc.add_paragraph(
        "1. Phân hệ Cửa hàng & Mua sắm (Customer Storefront):\n"
        "• Danh mục & Lọc thông minh: Hỗ trợ tìm kiếm từ khóa không phân biệt hoa thường, bảo vệ ký tự đặc biệt SQL (%, _); lọc theo danh mục phẳng; lọc khoảng giá min_price - max_price linh hoạt (tự động hoán vị nếu nhập min > max kèm cảnh báo); sắp xếp theo giá tăng dần, giá giảm dần, mới nhất.\n"
        "• Chi tiết sản phẩm & Đánh giá: Hiển thị đầy đủ thông tin, ảnh, giá, tồn kho; tính toán số sao trung bình động và hiển thị danh sách nhận xét của khách hàng.\n"
        "• Giỏ hàng Session Real-time: Giỏ hàng lưu trữ an toàn trong Flask session; hỗ trợ tương tác không cần tải lại trang với thông báo Toast mượt mà.\n"
        "• Đặt hàng Checkout: Biểu mẫu CheckoutForm (Flask-WTF) kiểm tra tính hợp lệ của họ tên, địa chỉ và định dạng số điện thoại Việt Nam (+84 hoặc 0x). Hỗ trợ cả khách đã đăng nhập và khách vãng lai.\n"
        "• Lịch sử đơn hàng cá nhân: Trang /my-orders và /my-orders/<id> cho phép khách hàng theo dõi trạng thái giao hàng của các đơn do mình đặt."
    )
    doc.add_paragraph(
        "2. Phân hệ Quản trị & Vận hành (Admin & Operations):\n"
        "• Dashboard thống kê: Truy vấn dữ liệu thực tế từ database tính toán tổng số sản phẩm, tổng đơn hàng, doanh thu thực tế từ các đơn hoàn thành, phân tích số lượng đơn theo từng trạng thái, và đưa ra danh sách cảnh báo sản phẩm sắp hết hàng (tồn <= 5).\n"
        "• Quản lý Sản phẩm: Giao diện quản lý toàn diện cho phép Admin thêm mới, chỉnh sửa thông tin, giá, tồn kho, ảnh và chuyển đổi trạng thái ẩn/hiện sản phẩm. Nhân viên Staff bị chặn truy cập module này.\n"
        "• Quản lý Đơn hàng: Cho phép Admin và Staff tìm kiếm đơn theo mã, tên khách hàng hoặc SĐT; lọc theo trạng thái đơn hàng; xem chi tiết từng dòng sản phẩm và thực hiện chuyển trạng thái (Mới -> Đang xử lý -> Hoàn thành / Hủy)."
    )
    doc.add_paragraph(
        "3. Phân hệ Xác thực & An toàn thông tin (Auth & Security):\n"
        "• Xác thực người dùng bằng Flask-Login, băm mật khẩu bằng thuật toán PBKDF2/SHA256 thông qua Werkzeug Security.\n"
        "• Điều hướng sau đăng nhập thông minh (redirect_by_role): Tự động chuyển Admin/Staff về /admin và Customer về trang chủ / danh mục mua sắm.\n"
        "• Cơ chế chống CSRF (Cross-Site Request Forgery): Bật WTF_CSRF_ENABLED trên toàn bộ ứng dụng; ngoại lệ riêng biệt cho REST API dựa trên token JWT.\n"
        "• Cấu hình Cookie phiên bảo mật: SESSION_COOKIE_HTTPONLY = True ngăn chặn tấn công XSS đánh cắp session; SESSION_COOKIE_SAMESITE = 'Lax' chống tấn công giả mạo yêu cầu chéo site."
    )

    add_h2("2.6. Đặc tả REST API & Cơ chế Xác thực JWT")
    doc.add_paragraph(
        "Dự án cung cấp 7 endpoints RESTful chuẩn mực, đáp ứng đầy đủ yêu cầu số 5 của môn học (tối thiểu 3 endpoints có JWT). "
        "Các API công khai trả về dữ liệu danh mục hàng hóa, trong khi các API quản lý và tra cứu đơn hàng bắt buộc phải gửi kèm "
        "tiêu đề: Authorization: Bearer <access_token>:"
    )

    api_endpoints = [
        ("GET /api/health", "Public", "None", "JSON trạng thái hoạt động của hệ thống.", "200 OK"),
        ("GET /api/products", "Public", "q, category, sort, min_price, max_price, page, per_page", "Danh sách sản phẩm có phân trang, số lượng, siêu dữ liệu.", "200 OK, 400 Bad Request"),
        ("GET /api/products/<id>", "Public", "None", "Chi tiết sản phẩm chỉ định theo mã ID.", "200 OK, 404 Not Found"),
        ("POST /api/auth/token", "Public", "email, password (JSON Body)", "Cấp access_token JWT (thời hạn 30 phút) và thông tin cơ bản của user.", "200 OK, 400, 401 Unauthorized"),
        ("GET /api/orders", "JWT Required", "page, per_page", "Danh sách đơn hàng (Admin/Staff xem tất cả; Customer chỉ xem đơn của mình).", "200 OK, 401 Unauthorized"),
        ("GET /api/orders/<id>", "JWT Required", "None", "Chi tiết đơn hàng kèm danh sách chi tiết mặt hàng và người nhận (Kiểm tra quyền sở hữu).", "200 OK, 403 Forbidden, 404"),
        ("PUT /api/orders/<id>/status", "JWT Required (Admin/Staff)", "status: 0, 1, 2, 3 (JSON Body)", "Cập nhật trạng thái đơn hàng (Chỉ dành cho Admin và Staff).", "200 OK, 400, 403, 404")
    ]
    add_custom_table(["Endpoint & HTTP Method", "Phân quyền (Auth)", "Tham số đầu vào", "Nội dung phản hồi dữ liệu (Response)", "Mã trạng thái HTTP"], api_endpoints, [1.8, 1.2, 1.2, 1.5, 0.8])

    add_h2("2.7. Tương tác động AJAX / Fetch API (Real-time Cart & UI Updates)")
    doc.add_paragraph(
        "Hệ thống tích hợp công nghệ JavaScript Fetch API hiện đại tại tệp static/js/cart.js nhằm mang lại trải nghiệm thương mại điện tử chuyên nghiệp:\n"
        "• Thêm vào giỏ tức thời: Khách hàng bấm 'Thêm vào giỏ' ở bất kỳ đâu, hệ thống gửi yêu cầu bất đồng bộ (POST), cập nhật ngay huy hiệu số lượng giỏ hàng trên thanh điều hướng (navbar badge) kèm thông báo Toast nổi mà không cần load lại trang.\n"
        "• Kỹ thuật Debounce khi cập nhật số lượng: Khi người dùng bấm tăng/giảm số lượng liên tục, mã nguồn JavaScript áp dụng kỹ thuật Debounce (trì hoãn gửi request trong một khoảng thời gian ngắn) để gom cụm các thao tác, tránh gửi dồn dập hàng chục request làm quá tải máy chủ.\n"
        "• Cơ chế Rollback UI thông minh: Nếu khách hàng nhập số lượng vượt quá số lượng hàng tồn kho thực tế trong CSDL, máy chủ trả về mã lỗi 409 Conflict. JavaScript sẽ lập tức hoàn tác (rollback) số lượng trên giao diện về giá trị hợp lệ trước đó và hiển thị thông báo lỗi rõ ràng."
    )

    add_h2("2.8. Cơ chế An toàn Dữ liệu & Chống Race Condition khi Checkout")
    doc.add_paragraph(
        "Một trong những thách thức lớn nhất của các ứng dụng bán hàng là nguy cơ bán âm hàng (Over-selling) khi nhiều khách hàng "
        "cùng bấm thanh toán một sản phẩm sắp hết hàng tại cùng một thời điểm. Dự án đã giải quyết triệt để vấn đề này trong cart_routes.py "
        "bằng giải pháp khóa bi quan (Pessimistic Locking) kết hợp Giao dịch nguyên tử (Atomic Database Transaction):"
    )
    add_code(
        "# Trích đoạn xử lý giao dịch nguyên tử trong app/shop/cart_routes.py:\n"
        "try:\n"
        "    for item in cart_items:\n"
        "        # Khóa dòng dữ liệu sản phẩm trong CSDL để tránh xung đột đồng thời\n"
        "        product = db.session.execute(\n"
        "            db.select(SanPham)\n"
        "            .where(SanPham.MASANPHAM == item['product'].MASANPHAM)\n"
        "            .with_for_update()\n"
        "        ).scalar_one_or_none()\n"
        "        \n"
        "        if product.SOLUONGTON < item['quantity']:\n"
        "            raise CheckoutError(f'Sản phẩm {product.TENSPH} không đủ số lượng tồn kho!')\n"
        "        \n"
        "        # Trừ kho ngay trong transaction\n"
        "        product.SOLUONGTON -= item['quantity']\n"
        "    \n"
        "    # Thêm đơn hàng và chi tiết đơn hàng\n"
        "    db.session.commit()\n"
        "    session.pop('cart', None) # Chỉ xóa giỏ hàng khi transaction thành công 100%\n"
        "except Exception:\n"
        "    db.session.rollback()     # Hoàn tác dữ liệu an toàn nếu có lỗi xảy ra"
    )

    doc.add_page_break()

    # =========================================================================
    # PHẦN III: HƯỚNG DẪN CÀI ĐẶT & VẬN HÀNH (CÁCH CHẠY)
    # =========================================================================
    add_h1("PHẦN III: HƯỚNG DẪN CÀI ĐẶT & VẬN HÀNH (CÁCH CHẠY)")

    add_h2("3.1. Yêu cầu môi trường chuẩn bị (Prerequisites)")
    doc.add_paragraph(
        "Để cài đặt và vận hành hệ thống một cách trơn tru, máy tính của người dùng hoặc ban giám khảo cần đáp ứng các yêu cầu sau:\n"
        "• Hệ điều hành: Windows 10/11, macOS, hoặc Linux (khuyến nghị có hỗ trợ Docker Desktop & WSL2 trên Windows).\n"
        "• Môi trường Python: Python phiên bản 3.12+ (đã tích hợp sẵn pip).\n"
        "• Môi trường Container: Docker Desktop và Docker Compose (phiên bản v2 trở lên).\n"
        "• Trình điều khiển cơ sở dữ liệu: ODBC Driver 18 for SQL Server (đã được cấu hình tự động trong Dockerfile)."
    )

    add_h2("3.2. Hướng dẫn chạy ứng dụng Local với SQLite (Development Mode)")
    doc.add_paragraph(
        "Chế độ chạy cục bộ với SQLite được tối ưu hóa cho việc phát triển tính năng, kiểm thử đơn vị nhanh mà không đòi hỏi phải cài đặt SQL Server phức tạp:"
    )

    doc.add_paragraph("Bước 1: Mở PowerShell tại thư mục gốc của dự án và khởi tạo môi trường ảo Python:")
    add_code(
        "# Tạo môi trường ảo\n"
        "python -m venv .venv\n\n"
        "# Kích hoạt môi trường ảo trên Windows PowerShell\n"
        ".\\.venv\\Scripts\\Activate.ps1"
    )

    doc.add_paragraph("Bước 2: Cài đặt toàn bộ các gói thư viện phụ thuộc:")
    add_code("python -m pip install -r requirements.txt")

    doc.add_paragraph("Bước 3: Thiết lập tệp cấu hình môi trường (.env):")
    add_code(
        "# Sao chép file mẫu\n"
        "Copy-Item .env.example .env\n\n"
        "# Nội dung cấu hình cơ bản trong .env:\n"
        "SECRET_KEY=dev-secret-key-pwd301-miniecommerce\n"
        "JWT_SECRET_KEY=jwt-dev-secret-key-pwd301\n"
        "DATABASE_URL=sqlite:///dev.db"
    )

    doc.add_paragraph("Bước 4: Khởi tạo cấu trúc bảng CSDL, nạp dữ liệu mẫu và tạo tài khoản thử nghiệm:")
    add_code(
        "# Khởi tạo schema và nạp 4 danh mục cùng 20 sản phẩm mẫu\n"
        "python seed.py\n\n"
        "# Khởi tạo các tài khoản demo (Admin, Staff, Customer)\n"
        "python create_test_users.py"
    )

    doc.add_paragraph("Bước 5: Khởi động máy chủ Flask và truy cập website:")
    add_code(
        "python run.py\n\n"
        "# Mở trình duyệt web và truy cập địa chỉ:\n"
        "http://127.0.0.1:5000"
    )

    add_h2("3.3. Hướng dẫn triển khai Production với Docker & Microsoft SQL Server 2022")
    doc.add_paragraph(
        "Đây là phương thức triển khai hoàn chỉnh chuẩn doanh nghiệp đáp ứng tiêu chuẩn bắt buộc số 1 và số 9 của môn học PWD301. "
        "Toàn bộ ứng dụng web Flask (chạy qua máy chủ Gunicorn) và CSDL Microsoft SQL Server 2022 được đóng gói trong 2 container độc lập "
        "kết nối qua mạng nội bộ Docker bridge:"
    )

    doc.add_paragraph("Bước 1: Cấu hình biến môi trường mật khẩu an toàn trong tệp .env:")
    add_code(
        "SECRET_KEY=production-super-strong-flask-secret-pwd301\n"
        "JWT_SECRET_KEY=production-super-strong-jwt-secret-pwd301\n"
        "MSSQL_SA_PASSWORD=Password123!Secure\n"
        "DATABASE_URL=mssql+pyodbc://sa:Password123!Secure@db:1433/MiniEcommerceDB?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
    )

    doc.add_paragraph("Bước 2: Build Docker Image cho dịch vụ Web Flask:")
    add_code("docker compose build web")

    doc.add_paragraph("Bước 3: Khởi động container Microsoft SQL Server 2022:")
    add_code(
        "docker compose up -d db\n\n"
        "# Đợi khoảng 10-15 giây để dịch vụ SQL Server hoàn tất quá trình khởi động nội bộ"
    )

    doc.add_paragraph("Bước 4: Bootstrap cơ sở dữ liệu MiniEcommerceDB và các bảng ứng dụng:")
    add_code("docker compose run --rm --no-deps web python -m scripts.bootstrap_db")

    doc.add_paragraph("Bước 5: Đánh dấu phiên bản migration CSDL ở bản mới nhất (Alembic Stamp Head):")
    add_code("docker compose run --rm --no-deps web flask --app run:app db stamp head")

    doc.add_paragraph("Bước 6: Nạp dữ liệu mẫu sản phẩm và tạo tài khoản kiểm thử vào SQL Server:")
    add_code(
        "# Nạp danh mục và sản phẩm mẫu\n"
        "docker compose run --rm --no-deps web python seed.py\n\n"
        "# Tạo tài khoản Admin, Staff và Customer\n"
        "docker compose run --rm --no-deps web python create_test_users.py"
    )

    doc.add_paragraph("Bước 7: Khởi động container Web Flask Gunicorn:")
    add_code(
        "docker compose up -d web\n\n"
        "# Kiểm tra trạng thái các container đang chạy:\n"
        "docker compose ps"
    )

    doc.add_paragraph("Bước 8: Truy cập ứng dụng tại cổng xuất bản (Published Port):")
    add_callout(
        "Mở trình duyệt web và truy cập: http://127.0.0.1:5050 (hoặc http://127.0.0.1:5000 nếu cấu hình cổng mặc định). "
        "Trang chủ hiển thị danh mục sản phẩm hoàn chỉnh lấy trực tiếp từ Microsoft SQL Server 2022.",
        title="ĐỊA CHỈ TRUY CẬP DOCKER:"
    )

    doc.add_paragraph("Thủ tục chuyển dữ liệu cũ từ SQLite sang SQL Server (Nếu có):")
    add_code(
        "# Bước sao lưu SQLite an toàn:\n"
        "python -c \"import sqlite3; src=sqlite3.connect('instance/dev.db'); dst=sqlite3.connect('instance/dev_backup.db'); src.backup(dst); dst.close(); src.close()\"\n\n"
        "# Thực thi script di chuyển dữ liệu vào container SQL Server:\n"
        "docker compose run --rm --no-deps --volume \"./instance/dev_backup.db:/tmp/legacy.db:ro\" web python -m scripts.migrate_sqlite_to_mssql"
    )

    add_h2("3.4. Hướng dẫn Chạy Kiểm thử Tự động (Automated Testing with Pytest)")
    doc.add_paragraph(
        "Dự án áp dụng triệt để phương pháp kiểm thử hướng chất lượng (Quality-Driven Engineering). "
        "Bộ kiểm thử tự động sử dụng CSDL SQLite in-memory biệt lập để đảm bảo tốc độ thực thi siêu tốc và không làm ảnh hưởng đến dữ liệu đang chạy:"
    )
    add_code(
        "# Chạy toàn bộ 144 test cases kiểm thử tự động:\n"
        "python -m pytest -v\n\n"
        "# Hoặc chạy rút gọn kèm thống kê tóm tắt:\n"
        "python -m pytest -q"
    )

    doc.add_paragraph("Kết quả kiểm thử thực tế mới nhất được xác minh:")
    test_results_data = [
        ("tests/test_admin.py", "22 tests", "Kiểm tra quyền truy cập Admin Dashboard, phân quyền Staff vs Admin, CRUD sản phẩm, chuyển trạng thái đơn hàng.", "PASSED 100%"),
        ("tests/test_api_auth.py", "6 tests", "Kiểm tra cấp phát JWT token, đăng nhập đúng/sai thông tin, mã hóa Bearer token, thời hạn token.", "PASSED 100%"),
        ("tests/test_api_orders.py", "14 tests", "Kiểm tra xem danh sách đơn theo role, chi tiết đơn, cập nhật trạng thái đơn hàng qua PUT API.", "PASSED 100%"),
        ("tests/test_api_products.py", "12 tests", "Kiểm tra lấy danh mục sản phẩm, lọc, tìm kiếm, phân trang và chi tiết sản phẩm qua GET API.", "PASSED 100%"),
        ("tests/test_cart_checkout.py", "18 tests", "Kiểm tra thêm/sửa/xóa giỏ hàng, Checkout atomic transaction, rollback khi thiếu hàng, bảo vệ đơn hàng.", "PASSED 100%"),
        ("tests/test_csrf_security.py", "9 tests", "Kiểm tra phòng chống tấn công CSRF trên các POST form, đảm bảo token hợp lệ mới được thực thi.", "PASSED 100%"),
        ("tests/test_models.py", "7 tests", "Kiểm tra khởi tạo quan hệ thực thể (ORM Relationships), tính toán thuộc tính và các phương thức UserMixin.", "PASSED 100%"),
        ("tests/test_products.py", "37 tests", "Kiểm tra tìm kiếm sản phẩm, hoán vị khoảng giá min/max, sắp xếp, phân trang và trạng thái ẩn/hiện.", "PASSED 100%"),
        ("tests/test_reviews.py", "17 tests", "Kiểm tra quan hệ Nhiều-Nhiều (M:N) DanhGia, ràng buộc 1 người/1 đánh giá, điểm sao 1-5, tính sao trung bình.", "PASSED 100%"),
        ("tests/test_stock_constraint.py", "2 tests", "Kiểm tra ràng buộc CHECK (SOLUONGTON >= 0) ở mức CSDL, chặn đứng lỗi tồn kho âm.", "PASSED 100%"),
        ("TỔNG KẾT TOÀN HỆ THỐNG", "144 tests", "Độ bao phủ toàn bộ các luồng nghiệp vụ Backend, Security, API và Database.", "144 PASSED (100%)")
    ]
    add_custom_table(["Tập tin kiểm thử", "Số lượng Test", "Mục tiêu kiểm thử & Nội dung nghiệp vụ", "Trạng thái"], test_results_data, [1.8, 0.9, 2.8, 1.0])

    add_h2("3.5. Danh mục Tài khoản Thử nghiệm Hệ thống (Test Accounts)")
    doc.add_paragraph(
        "Để phục vụ công tác chấm điểm và trình diễn (live demo), hệ thống đã tạo sẵn 3 tài khoản tương ứng với 3 vai trò phân quyền khác nhau:"
    )

    accounts_data = [
        ("Quản trị viên (Admin)", "admin@minishop.local", "Admin@123", "admin", "Toàn quyền quản trị hệ thống: Bảng điều khiển (Dashboard), Quản lý Sản phẩm (CRUD), Quản lý duyệt và đổi trạng thái Đơn hàng."),
        ("Nhân viên (Staff)", "staff@minishop.local", "Staff@123", "staff", "Nhân viên vận hành: Truy cập Dashboard thống kê, xem và đổi trạng thái Đơn hàng. Bị chặn quyền can thiệp vào Danh mục & Sản phẩm."),
        ("Khách hàng (Customer)", "customer@minishop.local", "Customer@123", "customer", "Khách hàng mua sắm: Xem sản phẩm, đánh giá/bình luận (Reviews), thêm giỏ hàng, đặt hàng (Checkout), xem lịch sử đơn cá nhân.")
    ]
    add_custom_table(["Vai trò tài khoản", "Email đăng nhập", "Mật khẩu mặc định", "Role trong DB", "Quyền hạn thực tế trên hệ thống"], accounts_data, [1.3, 1.5, 1.0, 0.9, 1.8])

    doc.add_page_break()

    # =========================================================================
    # PHẦN IV: TỔNG KẾT & ĐÁNH GIÁ ĐỀ TÀI
    # =========================================================================
    add_h1("PHẦN IV: TỔNG KẾT & ĐÁNH GIÁ ĐỀ TÀI (CONCLUSION & EVALUATION)")

    add_h2("4.1. Đánh giá Mức độ Hoàn thành so với Tiêu chuẩn Môn học PWD301")
    doc.add_paragraph(
        "Nhóm tự đánh giá dự án đã hoàn thành xuất sắc 100% các mục tiêu đề ra cho Topic 8 và thỏa mãn toàn bộ 12 tiêu chí bắt buộc "
        "của thang điểm đồ án môn học PWD301:"
    )

    rubric_evaluation = [
        ("1. Nền tảng Flask & SQL Server", "Sử dụng Flask 3.1.3 (Python 3.12+) kết hợp MS SQL Server 2022 làm CSDL chính thức.", "HOÀN THÀNH (10/10)"),
        ("2. Flask-SQLAlchemy & M:N", "Xây dựng 6 bảng CSDL, quan hệ M:N qua bảng DANHGIA (User - Product) kèm CHECK constraint.", "HOÀN THÀNH (10/10)"),
        ("3. Flask-WTF Forms & CSRF", "Bảo vệ CSRF toàn cục, xác thực CheckoutForm chặt chẽ (regex SĐT Việt Nam, địa chỉ, họ tên).", "HOÀN THÀNH (10/10)"),
        ("4. Flask-Login & RBAC 3 Roles", "Phân quyền chặt chẽ 3 vai trò: Admin, Staff, Customer cùng đối tượng Guest với decorators & hooks.", "HOÀN THÀNH (10/10)"),
        ("5. REST API (>= 3 Endpoints) & JWT", "Hiện thực 7 endpoints RESTful chuẩn JSON, bảo mật truy cập bằng JWT qua Flask-JWT-Extended.", "HOÀN THÀNH (10/10)"),
        ("6. AJAX / Fetch API Dynamic", "Tương tác giỏ hàng thời gian thực (thêm, cập nhật debounce, xóa, rollback khi hết hàng) không reload trang.", "HOÀN THÀNH (10/10)"),
        ("7. Jinja2 & Bootstrap 5 Responsive", "Kế thừa layout base.html, thiết kế responsive trên mọi kích thước màn hình, thẩm mỹ cao cấp.", "HOÀN THÀNH (10/10)"),
        ("8. Flask-Migrate & Seed Data", "5 phiên bản migration Alembic theo dõi tiến hóa DB; file seed.py nạp đầy đủ dữ liệu demo phong phú.", "HOÀN THÀNH (10/10)"),
        ("9. Đóng gói Container với Docker", "Dockerfile đa tầng, docker-compose.yml phối hợp 2 dịch vụ Web Gunicorn và Database MS SQL Server.", "HOÀN THÀNH (10/10)"),
        ("10. Nhật ký ứng dụng AI (AI Usage Log)", "Lưu vết chi tiết quy trình ứng dụng GitHub Copilot và Google Antigravity trong toàn bộ vòng đời dự án.", "HOÀN THÀNH (10/10)"),
        ("11. Quản lý mã nguồn trên Git", "Mã nguồn tổ chức khoa học trên GitHub/Git, lịch sử commit chuẩn conventional commit, README chi tiết.", "HOÀN THÀNH (10/10)"),
        ("12. Kiểm thử tự động & Báo cáo", "Hệ sinh thái 144 test cases pytest tự động đạt 100% tỷ lệ pass; chuẩn bị slide và kịch bản demo 20 phút.", "HOÀN THÀNH (10/10)")
    ]
    add_custom_table(["Tiêu chí đánh giá theo Rubric", "Hiện trạng triển khai thực tế của đề tài", "Đánh giá kết quả"], rubric_evaluation, [1.8, 3.4, 1.3])

    add_h2("4.2. Bảng Phân công Nhiệm vụ & Đóng góp của Thành viên")
    doc.add_paragraph(
        "Dự án được thực hiện với tinh thần phối hợp đồng đội chặt chẽ, phân chia nhiệm vụ rõ ràng dựa trên thế mạnh của từng thành viên:"
    )

    team_members = [
        ("Châu Lê Gia Bảo\n(Trưởng nhóm)", "• Thiết kế kiến trúc tổng thể dự án (Application Factory, Blueprints).\n• Cấu hình bảo mật hệ thống: CSRF Protection toàn cục, Cookie flags, Flask-Login setup.\n• Thiết kế và lập trình toàn bộ 7 REST API endpoints và xác thực bảo mật JWT.\n• Đóng gói Dockerfile, cấu hình docker-compose.yml đa dịch vụ và script chuyển dữ liệu.\n• Tích hợp kiểm thử hệ thống và viết tài liệu README.md hướng dẫn cài đặt.", "100%\n(25%)"),
        ("Hà Trung Kiên", "• Thiết kế mô hình CSDL quan hệ ERD chuẩn 3NF trên Microsoft SQL Server.\n• Xây dựng các lớp ORM Models: DanhMuc, SanPham, User, DonHang, ChiTietDonHang, DanhGia.\n• Thiết lập chuỗi migrations với Flask-Migrate (Alembic) và ràng buộc toàn vẹn CHECK/UNIQUE.\n• Xây dựng tầng dịch vụ product_service (tìm kiếm, lọc giá, phân trang) và review_service.\n• Viết script nạp dữ liệu mẫu seed.py và 37 test cases cho sản phẩm, 17 test cases cho review.", "100%\n(25%)"),
        ("Trần Vũ Hoàng Long", "• Xây dựng trung tâm quản trị Admin Panel với giao diện trực quan, chuyên nghiệp.\n• Thiết kế Admin Dashboard: truy vấn thống kê doanh thu thực, phân loại đơn, cảnh báo tồn kho.\n• Xây dựng chức năng Quản lý Sản phẩm (CRUD, ẩn/hiện, upload ảnh, kiểm tra giá/tồn kho).\n• Xây dựng chức năng Quản lý Đơn hàng: tìm kiếm đơn, lọc trạng thái, cập nhật trạng thái đơn.\n• Triển khai cơ chế phân quyền RBAC đa tầng giữa Admin và Staff (chặn Staff sửa sản phẩm).", "100%\n(25%)"),
        ("Minh Tuấn", "• Xây dựng module Giỏ hàng (Session-based Shopping Cart) và xử lý bất đồng bộ AJAX.\n• Lập trình JavaScript Fetch API (static/js/cart.js) với kỹ thuật Debounce và Rollback UI.\n• Xây dựng biểu mẫu CheckoutForm (Flask-WTF) và validation thông tin người nhận (SĐT, địa chỉ).\n• Hiện thực hóa giao dịch nguyên tử khi Checkout (Atomic Transaction) chống bán âm tồn kho.\n• Xây dựng giao diện và luồng xử lý theo dõi đơn hàng cá nhân của khách hàng (My Orders).", "100%\n(25%)")
    ]
    add_custom_table(["Họ tên & Vai trò", "Các công việc và phân hệ đảm nhiệm cụ thể", "Mức độ hoàn thành"], team_members, [1.5, 4.0, 1.0])

    add_h2("4.3. Nhật ký Ứng dụng Công cụ AI (AI Usage Log - Yêu cầu #10)")
    doc.add_paragraph(
        "Tuân thủ nghiêm túc Yêu cầu số 10 của môn học PWD301 ('Use AI tools and maintain an AI usage log'), "
        "nhóm đã ứng dụng các công cụ trí tuệ nhân tạo (GitHub Copilot và Google Antigravity Agentic AI) "
        "trong suốt quá trình kỹ nghệ phần mềm nhằm nâng cao năng suất và chất lượng mã nguồn:"
    )

    ai_logs = [
        ("Giai đoạn 1: Thiết kế Kiến trúc & CSDL", "Google Antigravity & Copilot", "Tư vấn thiết kế ERD 6 bảng, sinh mã khung SQLAlchemy models, cấu hình quan hệ Nhiều-Nhiều (M:N) DanhGia với ràng buộc UNIQUE và CHECK.", "Tối ưu hóa cấu trúc CSDL đạt chuẩn 3NF, giảm thiểu rủi ro sai sót trong định nghĩa khóa ngoại và ràng buộc toàn vẹn."),
        ("Giai đoạn 2: Lập trình Backend & Bảo mật", "GitHub Copilot", "Hỗ trợ viết mã xử lý giao dịch nguyên tử (Atomic Transaction) với khóa dòng with_for_update() khi checkout; cấu hình CSRF Protection và Flask-JWT-Extended.", "Ngăn chặn triệt để nguy cơ Race Condition khi mua hàng đồng thời; đảm bảo 100% các endpoint được bảo vệ đúng quyền hạn."),
        ("Giai đoạn 3: Lập trình Tương tác AJAX", "GitHub Copilot", "Sinh thuật toán Debounce trên JavaScript Fetch API để trì hoãn request cập nhật số lượng giỏ hàng; xử lý cập nhật navbar badge realtime.", "Nâng cao trải nghiệm người dùng, loại bỏ hiện tượng spam request gây quá tải CSDL."),
        ("Giai đoạn 4: Đóng gói Docker & Scripts", "Google Antigravity", "Sinh Dockerfile tối ưu đa tầng (multi-stage) cài đặt msodbcsql18 trên Debian 12 bookworm; viết script bootstrap_db.py và migrate_sqlite_to_mssql.py.", "Tự động hóa hoàn toàn quy trình triển khai môi trường SQL Server chỉ với 1 lệnh docker-compose."),
        ("Giai đoạn 5: Tự động hóa Kiểm thử (Pytest)", "Google Antigravity & Copilot", "Tạo sinh 144 kịch bản kiểm thử tự động (Unit & Integration Tests) bao phủ các trường hợp biên (edge cases): lỗi SĐT, hết hàng, sai role, CSRF token thiếu.", "Đạt độ bao phủ kiểm thử cao, phát hiện và sửa chữa kịp thời các lỗi tiềm ẩn trước khi tiến hành nghiệm thu đồ án.")
    ]
    add_custom_table(["Giai đoạn dự án", "Công cụ AI sử dụng", "Mục đích và phạm vi ứng dụng cụ thể", "Hiệu quả và giá trị mang lại"], ai_logs, [1.3, 1.2, 2.3, 1.7])

    add_h2("4.4. Đánh giá Ưu điểm, Hạn chế và Định hướng Phát triển")
    doc.add_paragraph(
        "1. Các ưu điểm nổi bật của hệ thống:\n"
        "• Độ tin cậy và chất lượng cao: 100% chức năng được kiểm chứng qua 144 test cases tự động, mã nguồn sạch, phân lớp rõ ràng (Models - Services - Routes - Templates).\n"
        "• An toàn dữ liệu tuyệt đối: Sử dụng giao dịch nguyên tử và khóa bi quan with_for_update() đảm bảo không bao giờ xảy ra lỗi âm hàng tồn kho.\n"
        "• Bảo mật vững chắc: Kiểm soát CSRF toàn diện, băm mật khẩu một chiều, mã hóa token JWT, thiết lập cookie an toàn.\n"
        "• Trải nghiệm khách hàng vượt trội: Thao tác giỏ hàng tức thời không reload trang nhờ AJAX/Fetch API kết hợp Debounce thông minh.\n"
        "• Khả năng đóng gói và nhân bản dễ dàng: Triển khai toàn bộ hệ thống bằng Docker Compose một cách nhanh chóng trên bất kỳ môi trường nào."
    )
    doc.add_paragraph(
        "2. Một số hạn chế hiện tại:\n"
        "• Chưa tích hợp cổng thanh toán trực tuyến thực tế (do phạm vi Topic 8 chỉ yêu cầu mô phỏng quy trình đặt hàng COD).\n"
        "• Lịch sử đơn hàng: Cột TONGGIATRI lưu đúng số tiền lúc đặt hàng, tuy nhiên chi tiết đơn hàng cũ hiển thị giá theo bảng sản phẩm hiện tại do bảng CHITIETDONHANG chưa có cột DONGIALUCBAN riêng biệt.\n"
        "• Hệ thống thông báo chưa tích hợp dịch vụ gửi Email xác nhận đơn hàng tự động."
    )
    doc.add_paragraph(
        "3. Định hướng phát triển mở rộng trong tương lai:\n"
        "• Tích hợp cổng thanh toán trực tuyến (VNPay / Momo / ZaloPay Sandbox) hoàn thiện trải nghiệm mua sắm không tiền mặt.\n"
        "• Bổ sung cột DONGIA_MUA vào bảng CHITIETDONHANG nhằm lưu vết lịch sử giá cố định tại thời điểm đặt hàng.\n"
        "• Tích hợp dịch vụ gửi Email tự động (SendGrid / Celery + Redis) để gửi hóa đơn điện tử cho khách hàng ngay sau khi đặt hàng thành công.\n"
        "• Ứng dụng trí tuệ nhân tạo (AI Recommendation System) để gợi ý các sản phẩm liên quan dựa trên thói quen duyệt web của khách hàng."
    )

    doc.add_paragraph("\n")
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_date = p_sign.add_run("Đà Nẵng, ngày 23 tháng 10 năm 2026\n")
    r_date.italic = True
    r_group = p_sign.add_run("ĐẠI DIỆN NHÓM THỰC HIỆN ĐỀ TÀI TOPIC 8\n")
    r_group.bold = True
    r_group.font.color.rgb = primary_color
    r_leader = p_sign.add_run("Châu Lê Gia Bảo (Nhóm trưởng)\n")
    r_leader.bold = True

    # Save document
    output_filename = "Bao_Cao_De_Tai_Topic_8_MiniEcommerce.docx"
    doc.save(output_filename)
    print("SUCCESS: Created Word document:", output_filename)

if __name__ == "__main__":
    build_document()
