import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User


def login_user(client, user):
    """Giả lập đăng nhập qua Flask-Login session transaction."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.MANGUOIDUNG)
        sess["_fresh"] = True


def test_change_password_requires_login(client):
    """Khách chưa đăng nhập bị chuyển hướng về trang login."""
    res = client.get("/auth/change-password")
    assert res.status_code == 302
    assert "/auth/login" in res.headers.get("Location", "")


def test_change_password_page_loads(client, app):
    """Người dùng đã đăng nhập truy cập được form đổi mật khẩu."""
    with app.app_context():
        user = User(
            HOTEN="Test Pass User",
            EMAIL="passuser@example.com",
            PASSWORD_HASH=generate_password_hash("OldPass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.get("/auth/change-password")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Đổi Mật Khẩu" in html
    assert "old_password" in html
    assert "new_password" in html
    assert "confirm_password" in html


def test_change_password_missing_fields(client, app):
    """Kiểm tra thiếu trường dữ liệu."""
    with app.app_context():
        user = User(
            HOTEN="Test Pass User",
            EMAIL="passuser2@example.com",
            PASSWORD_HASH=generate_password_hash("OldPass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.post("/auth/change-password", data={
        "old_password": "",
        "new_password": "NewPass@123",
        "confirm_password": "NewPass@123",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "Vui lòng điền đầy đủ" in html


def test_change_password_wrong_current_password(client, app):
    """Kiểm tra nhập sai mật khẩu hiện tại."""
    with app.app_context():
        user = User(
            HOTEN="Test Pass User",
            EMAIL="passuser3@example.com",
            PASSWORD_HASH=generate_password_hash("OldPass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.post("/auth/change-password", data={
        "old_password": "WrongPassword",
        "new_password": "NewPass@123",
        "confirm_password": "NewPass@123",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "Mật khẩu hiện tại không chính xác" in html


def test_change_password_short_new_password(client, app):
    """Kiểm tra mật khẩu mới ngắn hơn 6 ký tự."""
    with app.app_context():
        user = User(
            HOTEN="Test Pass User",
            EMAIL="passuser4@example.com",
            PASSWORD_HASH=generate_password_hash("OldPass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.post("/auth/change-password", data={
        "old_password": "OldPass@123",
        "new_password": "123",
        "confirm_password": "123",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "ít nhất 6 ký tự" in html


def test_change_password_mismatched_confirm(client, app):
    """Kiểm tra xác nhận mật khẩu không khớp."""
    with app.app_context():
        user = User(
            HOTEN="Test Pass User",
            EMAIL="passuser5@example.com",
            PASSWORD_HASH=generate_password_hash("OldPass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.post("/auth/change-password", data={
        "old_password": "OldPass@123",
        "new_password": "NewPass@123",
        "confirm_password": "DifferentPass@123",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "không khớp" in html


def test_change_password_same_as_old(client, app):
    """Kiểm tra mật khẩu mới trùng mật khẩu cũ."""
    with app.app_context():
        user = User(
            HOTEN="Test Pass User",
            EMAIL="passuser6@example.com",
            PASSWORD_HASH=generate_password_hash("OldPass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.post("/auth/change-password", data={
        "old_password": "OldPass@123",
        "new_password": "OldPass@123",
        "confirm_password": "OldPass@123",
    })
    assert res.status_code == 400
    html = res.get_data(as_text=True)
    assert "không được trùng" in html


def test_change_password_success(client, app):
    """Đổi mật khẩu thành công và xác thực mật khẩu mới."""
    with app.app_context():
        user = User(
            HOTEN="Test Pass User",
            EMAIL="passuser7@example.com",
            PASSWORD_HASH=generate_password_hash("OldPass@123"),
            ROLE="customer",
            TRANGTHAIND=1,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.MANGUOIDUNG

    user = db.session.get(User, user_id)
    login_user(client, user)

    res = client.post("/auth/change-password", data={
        "old_password": "OldPass@123",
        "new_password": "BrandNewPass@456",
        "confirm_password": "BrandNewPass@456",
    }, follow_redirects=True)

    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Đổi mật khẩu thành công" in html

    # Kiểm tra database cập nhật đúng hash mới
    with app.app_context():
        updated_user = db.session.get(User, user_id)
        assert check_password_hash(updated_user.PASSWORD_HASH, "BrandNewPass@456")
        assert not check_password_hash(updated_user.PASSWORD_HASH, "OldPass@123")
