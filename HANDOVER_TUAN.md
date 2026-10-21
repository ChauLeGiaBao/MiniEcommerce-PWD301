# Bàn giao phần Tuấn — MiniEcommerce-PWD301

## Phạm vi
Chỉ thực hiện các task TU01–TU07 trong `Cong_viec_con_lai_Tuan.docx`. Không sửa `base.html`, Auth/API của Bảo, Product/DB của Kiên hoặc Admin của Long. Không push lên GitHub.

## File thay đổi thuộc phạm vi Tuấn
- `app/shop/cart_routes.py`: kiểm tra quantity nguyên, xử lý checkout bằng một transaction, chỉ xóa cart sau commit, thêm `/my-orders` và `/my-orders/<order_id>` lọc theo user, ngăn tài khoản đăng nhập dùng `last_order_id` guest để xem đơn không thuộc guest.
- `app/static/js/cart.js`: auto-save quantity theo debounce, tuần tự hóa request theo input, bỏ qua response lỗi thời, rollback UI khi server từ chối, gửi CSRF header khi trang cung cấp token.
- `app/templates/cart.html`: giữ UI Cart AJAX, thêm hidden CSRF token vào các form Update/Remove.
- `app/shop/forms.py` (mới): `CheckoutForm` Flask-WTF và validation họ tên/địa chỉ/số điện thoại.
- `app/templates/checkout.html`: dùng CheckoutForm, hiển thị lỗi validation và giữ dữ liệu nhập.
- `app/templates/my_orders.html` (mới), `app/templates/my_order_detail.html` (mới): danh sách và chi tiết đơn của Customer.
- `tests/test_cart_checkout.py`: test checkout thành công, số điện thoại sai, quantity sai, hết hàng, truy cập Order Success sai quyền và lỗi commit/rollback.

## Kiểm tra đã thực hiện
- `node --check app/static/js/cart.js`: PASS.
- `python -m compileall -q app tests`: PASS (kiểm tra cú pháp, không phải test nghiệp vụ).
- `python -m pytest tests/test_cart_checkout.py -q`: CHƯA CHẠY ĐƯỢC trong môi trường hiện tại vì thiếu Flask (`ModuleNotFoundError: No module named 'flask'`). Không tuyên bố pytest PASS.

## Còn phụ thuộc / chưa nghiệm thu
1. `app/__init__.py` hiện vẫn có `user_loader` tạm trả `None`; Bảo cần tích hợp Auth thật trước khi nghiệm thu My Orders và quyền Customer.
2. Chưa bật `CSRFProtect` toàn cục trong bản này để tránh làm hỏng POST của Product/Admin/Auth. Checkout dùng `form.hidden_tag()`; Cart có hidden token và JS gửi header khi token hiện diện. Cần Bảo chốt cấu hình CSRF chung, Kiên thêm token vào Product form và Long thêm token vào Admin form trước khi bật bảo vệ toàn cục.
3. `with_for_update()` chưa được xác minh khóa hàng đúng trên SQL Server. Cần DB test độc lập để kiểm tra hai checkout cạnh tranh cùng sản phẩm.
4. Chưa chạy browser E2E, chưa có ảnh/video demo hoặc log pytest do môi trường thiếu dependency.
5. Chưa sửa `base.html`; Bảo cần thêm link navbar “Đơn hàng của tôi”.

Bản ZIP này là bản làm việc riêng để review, không phải xác nhận nghiệm thu hoàn chỉnh và không có thay đổi nào được push lên GitHub.
