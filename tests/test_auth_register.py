import pytest
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models import User


def test_get_register_page(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Tạo Tài Khoản" in html
    assert "full_name" in html
    assert "email" in html
    assert "password" in html
    assert "confirm_password" in html


def test_register_success(client, app):
    response = client.post("/auth/register", data={
        "full_name": "Nguyễn Văn Test",
        "email": "test-reg@example.com",
        "phone": "0987654321",
        "password": "Password@123",
        "confirm_password": "Password@123",
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Đăng ký tài khoản thành công" in html

    with app.app_context():
        user = User.query.filter_by(EMAIL="test-reg@example.com").first()
        assert user is not None
        assert user.HOTEN == "Nguyễn Văn Test"
        assert user.SDT == "0987654321"
        assert user.ROLE == "customer"
        assert user.TRANGTHAIND == 1
        assert check_password_hash(user.PASSWORD_HASH, "Password@123")


def test_register_missing_fields(client):
    response = client.post("/auth/register", data={
        "full_name": "",
        "email": "test@example.com",
        "password": "Password@123",
        "confirm_password": "Password@123",
    })
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Vui lòng điền đầy đủ" in html


def test_register_invalid_email(client):
    response = client.post("/auth/register", data={
        "full_name": "Test User",
        "email": "invalid-email-address",
        "password": "Password@123",
        "confirm_password": "Password@123",
    })
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "email không hợp lệ" in html.lower()


def test_register_short_password(client):
    response = client.post("/auth/register", data={
        "full_name": "Test User",
        "email": "valid@example.com",
        "password": "123",
        "confirm_password": "123",
    })
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "ít nhất 6 ký tự" in html


def test_register_mismatched_passwords(client):
    response = client.post("/auth/register", data={
        "full_name": "Test User",
        "email": "valid@example.com",
        "password": "Password@123",
        "confirm_password": "DifferentPassword@123",
    })
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Mật khẩu xác nhận không khớp" in html


def test_register_duplicate_email(client, app):
    # First registration
    client.post("/auth/register", data={
        "full_name": "User One",
        "email": "duplicate@example.com",
        "password": "Password@123",
        "confirm_password": "Password@123",
    })

    # Log out
    client.post("/auth/logout")

    # Second registration with same email
    response = client.post("/auth/register", data={
        "full_name": "User Two",
        "email": "duplicate@example.com",
        "password": "Password@456",
        "confirm_password": "Password@456",
    })
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "đã được sử dụng" in html


def test_register_redirect_when_logged_in(client):
    # Register and automatically logged in
    client.post("/auth/register", data={
        "full_name": "Logged In User",
        "email": "logged@example.com",
        "password": "Password@123",
        "confirm_password": "Password@123",
    })

    # Visiting /auth/register now should redirect to shop
    response = client.get("/auth/register")
    assert response.status_code == 302
    assert "/products" in response.headers["Location"]
