import time
import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth.routes import generate_reset_token, verify_reset_token
from app.extensions import db
from app.models import User


def login_user(client, user):
    """Giả lập đăng nhập qua session transaction."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.MANGUOIDUNG)
        sess["_fresh"] = True


def test_forgot_password_page_loads_for_guest(client):
    """Khách chưa đăng nhập truy cập được trang Quên mật khẩu."""
    res = client.get("/auth/forgot-password")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Quên Mật Khẩu" in html
    assert 'name="email"' in html
    assert 'name="csrf_token"' in html


def test_forgot_password_redirects_if_already_logged_in(client, app):
    """Người dùng đã đăng nhập thì chuyển hướng về trang sản phẩm."""
    with app.app_context():
        user = User(
            HOTEN="Active Customer",
            EMAIL="active_cust@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.get("/auth/forgot-password")
    assert res.status_code == 302
    assert "/products" in res.headers.get("Location", "")


def test_forgot_password_empty_email(client):
    """Yêu cầu quên mật khẩu không có email trả về lỗi 400."""
    res = client.post("/auth/forgot-password", data={"email": "   "})
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "Vui lòng nhập địa chỉ email" in html


def test_forgot_password_nonexistent_email_returns_neutral_message(client):
    """Email không tồn tại trả về thông báo trung lập, không làm lộ thông tin tài khoản."""
    res = client.post("/auth/forgot-password", data={"email": "ghost_user_999@example.com"})
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Nếu email tồn tại trong hệ thống" in html
    assert "Liên kết khôi phục" not in html


def test_forgot_password_inactive_user_returns_neutral_message(client, app):
    """Tài khoản bị khóa (TRANGTHAIND=0) không nhận được liên kết đặt lại."""
    with app.app_context():
        locked_user = User(
            HOTEN="Locked User",
            EMAIL="locked_reset@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=0,
        )
        db.session.add(locked_user)
        db.session.commit()

    res = client.post("/auth/forgot-password", data={"email": "locked_reset@example.com"})
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Nếu email tồn tại trong hệ thống" in html
    assert "Liên kết khôi phục" not in html


def test_forgot_password_success_generates_token_and_link(client, app):
    """Email hợp lệ của user hoạt động sẽ tạo link đặt lại mật khẩu trong môi trường test."""
    with app.app_context():
        user = User(
            HOTEN="Reset Test User",
            EMAIL="reset_valid@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()

    res = client.post("/auth/forgot-password", data={"email": "reset_valid@example.com"})
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Nếu email tồn tại trong hệ thống" in html
    assert "/auth/reset-password/" in html


def test_reset_password_page_loads_with_valid_token(client, app):
    """Trang đặt lại mật khẩu tải thành công khi có token hợp lệ."""
    with app.app_context():
        user = User(
            HOTEN="Reset Form User",
            EMAIL="reset_form@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user.EMAIL)

    res = client.get(f"/auth/reset-password/{token}")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Đặt Lại Mật Khẩu" in html
    assert 'name="new_password"' in html
    assert 'name="confirm_password"' in html


def test_reset_password_redirects_if_logged_in(client, app):
    """Người dùng đã đăng nhập thì không vào form reset-password."""
    with app.app_context():
        user = User(
            HOTEN="LoggedIn User",
            EMAIL="loggedin_reset@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user.EMAIL)
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.get(f"/auth/reset-password/{token}")
    assert res.status_code == 302
    assert "/products" in res.headers.get("Location", "")


def test_reset_password_invalid_tampered_token(client):
    """Token sai chữ ký hoặc bị sửa đổi sẽ bị từ chối và redirect về forgot-password."""
    res = client.get("/auth/reset-password/tampered_bad_token_12345")
    assert res.status_code == 302
    assert "/auth/forgot-password" in res.headers.get("Location", "")


def test_reset_password_expired_token(client, app):
    """Token hết hạn thời gian (max_age) sẽ bị từ chối."""
    with app.app_context():
        token = generate_reset_token("any_user@example.com")
        # Kiểm tra hàm xác thực với max_age=-1 để giả lập token quá hạn
        assert verify_reset_token(token, max_age=-1) is None


def test_reset_password_missing_fields(client, app):
    """Gửi form thiếu trường mật khẩu trả về 400."""
    with app.app_context():
        user = User(
            HOTEN="Missing Fields User",
            EMAIL="missing_pass@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user.EMAIL)

    res = client.post(f"/auth/reset-password/{token}", data={
        "new_password": "",
        "confirm_password": "",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "Vui lòng nhập đầy đủ" in html


def test_reset_password_too_short(client, app):
    """Mật khẩu mới ngắn hơn 6 ký tự trả về 400."""
    with app.app_context():
        user = User(
            HOTEN="Short Pass User",
            EMAIL="short_pass@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user.EMAIL)

    res = client.post(f"/auth/reset-password/{token}", data={
        "new_password": "123",
        "confirm_password": "123",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "phải có ít nhất 6 ký tự" in html


def test_reset_password_mismatched_confirmation(client, app):
    """Mật khẩu xác nhận không khớp trả về 400."""
    with app.app_context():
        user = User(
            HOTEN="Mismatch User",
            EMAIL="mismatch_pass@example.com",
            PASSWORD_HASH=generate_password_hash("Pass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user.EMAIL)

    res = client.post(f"/auth/reset-password/{token}", data={
        "new_password": "NewSecretPassword1",
        "confirm_password": "DifferentSecretPassword2",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "Xác nhận mật khẩu mới không khớp" in html


def test_reset_password_success_flow_and_can_login(client, app):
    """Quy trình đầy đủ: đặt lại mật khẩu thành công và đăng nhập được bằng mật khẩu mới."""
    with app.app_context():
        user = User(
            HOTEN="Success Reset User",
            EMAIL="success_reset@example.com",
            PASSWORD_HASH=generate_password_hash("OldPassword@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user.EMAIL)
        user_id = user.MANGUOIDUNG

    # 1. Gửi form đặt lại mật khẩu với NewPassword@456
    res = client.post(f"/auth/reset-password/{token}", data={
        "new_password": "NewPassword@456",
        "confirm_password": "NewPassword@456",
    })
    assert res.status_code == 302
    assert "/auth/login" in res.headers.get("Location", "")

    # 2. Kiểm tra password hash trong database đã thay đổi
    with app.app_context():
        updated_user = db.session.get(User, user_id)
        assert check_password_hash(updated_user.PASSWORD_HASH, "NewPassword@456")
        assert not check_password_hash(updated_user.PASSWORD_HASH, "OldPassword@123")

    # 3. Đăng nhập thử với mật khẩu cũ -> Thất bại 401
    res_old = client.post("/auth/login", data={
        "email": "success_reset@example.com",
        "password": "OldPassword@123"
    })
    assert res_old.status_code == 401

    # 4. Đăng nhập thử với mật khẩu mới -> Thành công 302
    res_new = client.post("/auth/login", data={
        "email": "success_reset@example.com",
        "password": "NewPassword@456"
    })
    assert res_new.status_code == 302
