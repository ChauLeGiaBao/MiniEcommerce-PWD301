
import re


def enable_csrf(app):
    """Enable CSRF protection during this test."""
    app.config["WTF_CSRF_ENABLED"] = True


def get_csrf_token(response):
    """Extract CSRF token from the base.html meta tag."""
    html = response.get_data(as_text=True)

    match = re.search(
        r'<meta\s+name="csrf-token"\s+content="([^"]+)"',
        html
    )

    assert match is not None, (
        "CSRF meta tag not found in rendered HTML"
    )

    return match.group(1)


def test_csrf_extension_initialized(app):
    """CSRFProtect must be registered with Flask."""
    assert "csrf" in app.extensions


def test_login_rejects_missing_csrf(app, client):
    """Login POST without CSRF token must fail."""
    enable_csrf(app)

    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 400


def test_login_rejects_invalid_csrf(app, client):
    """Login POST with invalid CSRF token must fail."""
    enable_csrf(app)

    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "wrong-password",
            "csrf_token": "invalid-csrf-token"
        }
    )

    assert response.status_code == 400


def test_login_accepts_valid_csrf(app, client):
    """Valid CSRF passes security check, then authentication runs."""
    enable_csrf(app)

    page = client.get("/auth/login")
    assert page.status_code == 200

    token = get_csrf_token(page)

    response = client.post(
        "/auth/login",
        data={
            "email": "unknown@example.com",
            "password": "wrong-password",
            "csrf_token": token
        }
    )

    # Authentication rejects credentials, not CSRF.
    assert response.status_code == 401


def test_cart_rejects_missing_csrf(app, client):
    """Adding to cart without CSRF token must fail."""
    enable_csrf(app)

    response = client.post(
        "/cart/add/1",
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json"
        }
    )

    assert response.status_code == 400


def test_cart_ajax_accepts_valid_csrf(app, client):
    """AJAX cart request with X-CSRFToken must work."""
    enable_csrf(app)

    page = client.get("/products")
    assert page.status_code == 200

    token = get_csrf_token(page)

    response = client.post(
        "/cart/add/1",
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
            "X-CSRFToken": token
        }
    )

    assert response.status_code == 200

    result = response.get_json()
    assert result["success"] is True


def test_checkout_rejects_missing_csrf(app, client):
    """Checkout POST without CSRF token must fail."""
    enable_csrf(app)

    response = client.post(
        "/checkout",
        data={
            "fullname": "Test Customer",
            "address": "Ho Chi Minh City",
            "phone": "0912345678"
        }
    )

    assert response.status_code == 400


def test_jwt_login_does_not_require_csrf(app, client):
    """
    JWT endpoint uses Authorization headers instead
    of cookie-based authentication.
    """
    enable_csrf(app)

    response = client.post(
        "/api/auth/token",
        json={
            "email": "unknown@example.com",
            "password": "wrong-password"
        }
    )

    # Request passes CSRF layer but credentials are invalid.
    assert response.status_code == 401


def test_logout_requires_post_and_csrf(app, client):
    """Logout cannot use GET and POST requires CSRF."""
    enable_csrf(app)

    get_response = client.get("/auth/logout")
    assert get_response.status_code == 405

    post_response = client.post("/auth/logout")
    assert post_response.status_code == 400
