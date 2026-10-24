# Nhật Ký Sử Dụng AI (AI Usage Log) — Đề Tài Topic 8 (Mini E-Commerce Store)

> **Môn học:** PWD301 — Lập trình ứng dụng Web với Python (Web App Development with Python)  
> **Học kỳ:** Fall 2026 (Học kỳ 5) — Trường Đại học FPT  
> **Nhóm sinh viên thực hiện:**
> - Châu Lê Gia Bảo (Nhóm trưởng)
> - Hà Trung Kiên
> - Trần Vũ Hoàng Long
> - Minh Tuấn  
> **Chính sách áp dụng:** Tuân thủ quy định sử dụng công cụ AI hỗ trợ học tập và phát triển phần mềm có trách nhiệm (Responsible AI & Academic Integrity).

---

## 1. Nguyên Tắc Sử Dụng AI Của Nhóm
1. **AI là trợ lý lập trình (Pair Programmer), không thay thế tư duy kỹ thuật:** Mọi đoạn mã nguồn do AI gợi ý đều được các thành viên trong nhóm rà soát (Code Review), chỉnh sửa theo kiến trúc chuẩn của dự án và chạy kiểm thử tự động xác thực (Verification First).
2. **Không commit thông tin nhạy cảm:** Không chia sẻ thông tin bí mật máy cá nhân, secret key, credential hoặc mật khẩu quản trị vào prompt.
3. **Độc lập kiểm thử:** Toàn bộ 156 test cases trong hệ thống Pytest được viết và chạy thực tế trên môi trường SQLite/SQL Server để bảo đảm độ tin cậy tuyệt đối trước khi bàn giao.

---

## 2. Bảng Nhật Ký Chi Tiết (Detailed AI Interaction Log)

| STT | Ngày | Thành viên | Công cụ AI | Mục tiêu & Tóm tắt Prompt | Kết quả do AI đề xuất | Phần mã nguồn / tài liệu áp dụng thực tế | Kiểm tra & Đánh giá của con người |
|:---:|:---:|:---|:---|:---|:---|:---|:---|
| 1 | 15/09/2026 | Châu Lê Gia Bảo | Google Antigravity (Gemini 2.5 Pro) | "Thiết kế kiến trúc thư mục Flask theo mô hình Application Factory (`create_app`) kết hợp Blueprints cho dự án Mini E-Commerce." | Đề xuất cấu trúc module: `app/shop`, `app/admin`, `app/auth`, `app/api`, `app/models`, `app/services` và cấu hình `config.py`. | Áp dụng toàn bộ khung thư mục dự án và file khởi tạo `app/__init__.py`. | Nhóm đã tái cấu trúc lại tên các module thành dạng phẳng, không lồng `app/blueprints/` để code gọn hơn. |
| 2 | 22/09/2026 | Châu Lê Gia Bảo | Google Antigravity (Gemini 2.5 Pro) | "Tạo các model SQLAlchemy cho SQL Server: DanhMuc, SanPham, DonHang, ChiTietDonHang, NguoiDung và quan hệ M:N DanhGia." | Code các file model trong `app/models/` với kiểu dữ liệu `Unicode`, `Numeric(18,2)` và các ràng buộc Foreign Key. | Áp dụng vào 6 file models trong `app/models/` và kịch bản di trú `migrations/`. | Bổ sung thêm ràng buộc `CK_SANPHAM_SOLUONGTON (SOLUONGTON >= 0)` và `CK_DANHGIA_SOSAO` để bảo vệ toàn vẹn dữ liệu ở tầng DB. |
| 3 | 02/10/2026 | Hà Trung Kiên | Google Antigravity | "Hiện thực hệ thống Authentication an toàn với Flask-Login, phân quyền 3 role (admin, staff, customer), mã hóa mật khẩu và chống CSRF, Open Redirect." | Đề xuất decorator `@admin_required`, middleware `@admin_bp.before_request`, hàm kiểm tra URL an toàn `is_safe_url()`, mật khẩu băm với `werkzeug.security`. | Áp dụng trong `app/auth/routes.py`, `app/admin/routes.py` và cấu hình `CSRFProtect` trên toàn app. | Đã kiểm tra và tinh chỉnh ma trận RBAC: Staff chỉ được xem dashboard và quản lý đơn, bị chặn 403 ở CRUD sản phẩm. |
| 4 | 08/10/2026 | Châu Lê Gia Bảo | Google Antigravity | "Viết logic giỏ hàng AJAX (Fetch API) không tải lại trang và cơ chế khóa bi quan (Pessimistic Locking) chống bán âm kho khi checkout." | Code JavaScript `cart.js` gửi Fetch kèm `X-CSRFToken`; code backend `with_for_update()` trong truy vấn SQLAlchemy khi đặt hàng. | Áp dụng vào `app/static/js/cart.js` và `app/shop/cart_routes.py`. | Kiểm thử đồng thời (concurrency simulation) và kiểm tra tương thích giữa SQLite (bỏ qua lock) và SQL Server (UPDLOCK). |
| 5 | 14/10/2026 | Trần Vũ Hoàng Long | Google Antigravity | "Xây dựng giao diện Admin Dashboard và các màn hình quản trị CRUD sản phẩm, cập nhật trạng thái đơn hàng." | Đề xuất layout Bootstrap 5 với thẻ tóm tắt doanh thu, biểu đồ thống kê đơn hàng, bảng lọc danh sách và form modal. | Áp dụng vào `app/templates/admin_dashboard.html`, `app/templates/admin_products.html`, `app/templates/admin_orders.html`. | Nhóm đã làm sạch logic tính toán doanh thu (tách rõ doanh thu tổng và doanh thu thực tế từ đơn hoàn thành). |
| 6 | 18/10/2026 | Minh Tuấn | Google Antigravity | "Xây dựng 7 RESTful API JSON có xác thực qua Flask-JWT-Extended (Bearer Token) cho Sản phẩm, Đơn hàng và Health check." | Cung cấp các endpoint: `POST /api/auth/token`, `GET /api/products`, `GET /api/products/<id>`, `GET /api/orders`, `GET /api/orders/<id>`, `PUT /api/orders/<id>/status`, `GET /api/health`. | Áp dụng vào `app/api/auth_routes.py`, `app/api/order_routes.py`, `app/api/routes.py`. | Tinh chỉnh bảo mật: `@jwt_required()` luôn truy vấn lại user từ DB để chặn ngay nếu tài khoản bị khóa (`TRANGTHAIND != 1`). |
| 7 | 21/10/2026 | Cả nhóm | Google Antigravity | "Soạn thảo kịch bản kiểm thử tự động toàn diện với Pytest bao quát CSRF, giỏ hàng, checkout, RBAC 3 vai trò và 7 REST API." | Đề xuất cấu trúc fixtures trong `tests/conftest.py`, các test case cô lập dữ liệu bằng SQLite in-memory. | Bổ sung thêm các bộ kiểm thử vào `tests/`, nâng tổng số test cases lên 156 bài test. | Chạy toàn bộ test trên môi trường thật: 156/156 bài kiểm thử đều PASS (kết quả thực tế: 156 passed in 6.64s). |
| 8 | 23/10/2026 | Châu Lê Gia Bảo | Google Antigravity | "Cấu hình Dockerfile đa tầng và docker-compose.yml khởi chạy đồng thời Flask Web App và SQL Server 2022." | File Dockerfile cài đặt ODBC Driver 18, gunicorn production server; docker-compose.yml cấu hình cổng 5050 và healthcheck DB. | Áp dụng vào `Dockerfile`, `docker-compose.yml`, `scripts/bootstrap_db.py`. | Rà soát và thêm biến kiểm tra bắt buộc trong docker-compose: `MSSQL_SA_PASSWORD`, `SECRET_KEY`, `JWT_SECRET_KEY`. |
| 9 | 24/10/2026 | Cả nhóm | Google Antigravity (Gemini 3.8 Flash) | "Đối chiếu báo cáo đồ án với mã nguồn thực tế theo góp ý của người chấm bài, sửa 13 điểm lệch kỹ thuật và viết lại báo cáo chuẩn." | Phân tích 7 trang nhận xét của người chấm, phát hiện sai sót về Bcrypt/Werkzeug, sai endpoint JWT, sai tên cột DB, cập nhật 156 test, ma trận RBAC 3 role. | Cập nhật script `scripts/generate_project_report_docx.py`, sinh lại file Word báo cáo và cập nhật tài liệu `docs/`. | Toàn bộ thành viên xác nhận báo cáo mới chuẩn xác 100% so với mã nguồn thực tế đang nộp. |
| 10 | 24/10/2026 | Cả nhóm | Google Antigravity | "Hoàn thiện mã nguồn: bổ sung tính năng Đổi mật khẩu (/auth/change-password) và KPI Tổng người dùng trên Admin Dashboard." | Đề xuất route `change_password`, template `change_password.html`, tính `user_count`/`customer_count` trong admin dashboard và viết bộ 9 unit tests. | Áp dụng vào `app/auth/routes.py`, `app/templates/change_password.html`, `app/admin/routes.py`, `app/templates/admin_dashboard.html`, `tests/test_auth_change_password.py`, `tests/test_admin.py`. | Chạy toàn bộ 165 bài kiểm thử: 165/165 passed in 8.55s. |

---

## 3. Tổng Kết Đóng Góp Của AI và Nỗ Lực Của Nhóm
- **Hiệu quả:** AI hỗ trợ đẩy nhanh tốc độ tạo khung ứng dụng (scaffolding), gợi ý cú pháp ORM phức tạp và soạn thảo nhanh các trường hợp kiểm thử biên (edge cases).
- **Trách nhiệm của sinh viên:** Toàn bộ tư duy logic nghiệp vụ, kiến trúc bảo mật chống tấn công OWASP, tích hợp cơ sở dữ liệu thật SQL Server 2022 và đảm bảo tính nhất quán của hệ thống đều do nhóm sinh viên trực tiếp thiết kế, kiểm tra và bảo vệ trước Hội đồng chấm thi.
