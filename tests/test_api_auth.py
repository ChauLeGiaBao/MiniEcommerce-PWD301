
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User


def make_user(role="customer", active=1):
    user = User(
        HOTEN="API Test User",
        EMAIL="api-test@example.com",
        PASSWORD_HASH=generate_password_hash("Test@123"),
        ROLE=role,
        TRANGTHAIND=active
    )
    db.session.add(user)
    db.session.commit()
    return user.MANGUOIDUNG


def test_jwt_login_success(client, app):
    with app.app_context():
        user_id = make_user()

    response = client.post("/api/auth/token", json={
        "email": "api-test@example.com",
        "password": "Test@123"
    })

    assert response.status_code == 200

    result = response.get_json()
    assert result["access_token"]
    assert result["token_type"] == "Bearer"
    assert result["expires_in"] == 1800
    assert result["user"]["id"] == user_id
    assert result["user"]["role"] == "customer"


def test_jwt_wrong_password(client, app):
    with app.app_context():
        make_user()

    response = client.post("/api/auth/token", json={
        "email": "api-test@example.com",
        "password": "wrong-password"
    })

    assert response.status_code == 401


def test_jwt_unknown_email(client):
    response = client.post("/api/auth/token", json={
        "email": "unknown@example.com",
        "password": "Test@123"
    })

    assert response.status_code == 401


def test_jwt_disabled_account(client, app):
    with app.app_context():
        make_user(active=0)

    response = client.post("/api/auth/token", json={
        "email": "api-test@example.com",
        "password": "Test@123"
    })

    assert response.status_code == 401


def test_jwt_missing_password(client):
    response = client.post("/api/auth/token", json={
        "email": "api-test@example.com"
    })

    assert response.status_code == 400


def test_jwt_invalid_json(client):
    response = client.post(
        "/api/auth/token",
        data="not-json",
        content_type="application/json"
    )

    assert response.status_code == 400
