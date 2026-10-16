
from datetime import date
from decimal import Decimal

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User, DonHang, ChiTietDonHang


def make_user(email, role="customer", active=1):
    user = User(
        HOTEN="Order API Tester",
        EMAIL=email,
        ROLE=role,
        TRANGTHAIND=active,
    )
    db.session.add(user)
    db.session.commit()
    return user.MANGUOIDUNG


def make_order(user_id):
    order = DonHang(
        MANGUOIDUNG=user_id,
        NGAYDAT=date(2026, 10, 16),
        TONGGIATRI=Decimal("44000000.00"),
        TRANGTHAI=0,
        HOTENNHAN="Test Recipient",
        DIACHIGIAO="Test Address",
        SDTNHAN="0901234567",
    )
    db.session.add(order)
    db.session.flush()

    db.session.add(
        ChiTietDonHang(
            MADONHANG=order.MADONHANG,
            MASANPHAM=1,
            SOLUONG=2,
        )
    )
    db.session.commit()
    return order.MADONHANG


def bearer(app, user_id):
    with app.app_context():
        token = create_access_token(identity=str(user_id))
    return {"Authorization": "Bearer " + token}


def test_orders_require_jwt(client):
    response = client.get("/api/orders")
    assert response.status_code == 401


def test_invalid_token(client):
    response = client.get(
        "/api/orders",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 422


def test_customer_sees_only_own_orders(client, app):
    with app.app_context():
        owner = make_user("owner@example.com")
        other = make_user("other@example.com")
        order_id = make_order(owner)
        make_order(other)
        make_order(None)

    response = client.get(
        "/api/orders",
        headers=bearer(app, owner)
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["count"] == 1
    assert result["data"][0]["id"] == order_id


def test_admin_sees_all_orders(client, app):
    with app.app_context():
        admin = make_user("admin@example.com", "admin")
        customer = make_user("customer@example.com")
        make_order(customer)
        make_order(None)

    response = client.get(
        "/api/orders",
        headers=bearer(app, admin)
    )

    assert response.status_code == 200
    assert response.get_json()["count"] == 2


def test_staff_sees_all_orders(client, app):
    with app.app_context():
        staff = make_user("staff@example.com", "staff")
        make_order(None)

    response = client.get(
        "/api/orders",
        headers=bearer(app, staff)
    )

    assert response.status_code == 200
    assert response.get_json()["count"] == 1


def test_customer_can_view_own_order(client, app):
    with app.app_context():
        owner = make_user("owner@example.com")
        order_id = make_order(owner)

    response = client.get(
        "/api/orders/{}".format(order_id),
        headers=bearer(app, owner)
    )

    assert response.status_code == 200

    result = response.get_json()
    assert result["id"] == order_id
    assert result["recipient"]["name"] == "Test Recipient"
    assert len(result["items"]) == 1
    assert result["items"][0]["quantity"] == 2


def test_customer_cannot_view_other_order(client, app):
    with app.app_context():
        owner = make_user("owner@example.com")
        other = make_user("other@example.com")
        order_id = make_order(other)

    response = client.get(
        "/api/orders/{}".format(order_id),
        headers=bearer(app, owner)
    )

    assert response.status_code == 403


def test_customer_cannot_update_status(client, app):
    with app.app_context():
        owner = make_user("owner@example.com")
        order_id = make_order(owner)

    response = client.put(
        "/api/orders/{}/status".format(order_id),
        json={"status": 2},
        headers=bearer(app, owner),
    )

    assert response.status_code == 403


def test_staff_can_update_status(client, app):
    with app.app_context():
        staff = make_user("staff@example.com", "staff")
        order_id = make_order(None)

    response = client.put(
        "/api/orders/{}/status".format(order_id),
        json={"status": 1},
        headers=bearer(app, staff),
    )

    assert response.status_code == 200
    assert response.get_json()["order"]["status"] == 1

    with app.app_context():
        order = db.session.get(DonHang, order_id)
        assert order.TRANGTHAI == 1


def test_admin_can_update_status(client, app):
    with app.app_context():
        admin = make_user("admin@example.com", "admin")
        order_id = make_order(None)

    response = client.put(
        "/api/orders/{}/status".format(order_id),
        json={"status": 2},
        headers=bearer(app, admin),
    )

    assert response.status_code == 200
    assert response.get_json()["order"]["status"] == 2


def test_invalid_status_rejected(client, app):
    with app.app_context():
        admin = make_user("admin@example.com", "admin")
        order_id = make_order(None)

    for invalid in [4, -1, True, "completed"]:
        response = client.put(
            "/api/orders/{}/status".format(order_id),
            json={"status": invalid},
            headers=bearer(app, admin),
        )
        assert response.status_code == 400

    with app.app_context():
        assert db.session.get(DonHang, order_id).TRANGTHAI == 0


def test_missing_order_returns_404(client, app):
    with app.app_context():
        admin = make_user("admin@example.com", "admin")

    response = client.get(
        "/api/orders/999999",
        headers=bearer(app, admin)
    )

    assert response.status_code == 404


def test_inactive_user_cannot_use_token(client, app):
    with app.app_context():
        inactive = make_user(
            "inactive@example.com",
            active=0,
        )

    response = client.get(
        "/api/orders",
        headers=bearer(app, inactive)
    )

    assert response.status_code == 401


def test_invalid_pagination(client, app):
    with app.app_context():
        admin = make_user("admin@example.com", "admin")

    response = client.get(
        "/api/orders?page=-1",
        headers=bearer(app, admin)
    )

    assert response.status_code == 400
