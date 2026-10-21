import os
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from app import create_app
from app.extensions import db
from app.models import SanPham, DonHang, ChiTietDonHang, User
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SQLALCHEMY_DATABASE_URI="sqlite://")
    with app.app_context():
        db.drop_all()
        db.create_all()
        product = SanPham(TENSPH="Test product", DONGIA=10000, SOLUONGTON=5, TRANGTHAISPH=1)
        db.session.add(product)
        db.session.commit()
        product_id = product.MASANPHAM
    with app.test_client() as test_client:
        yield test_client, product_id
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_add_update_remove_cart(client):
    c, product_id = client
    response = c.post(f"/cart/add/{product_id}", headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    assert response.status_code == 200
    assert response.get_json()["success"] is True
    with c.session_transaction() as sess:
        assert sess["cart"][str(product_id)] == 1

    response = c.post(f"/cart/update/{product_id}", json={"quantity": 3}, headers={"X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 200
    with c.session_transaction() as sess:
        assert sess["cart"][str(product_id)] == 3

    response = c.post(f"/cart/update/{product_id}", json={"quantity": 6}, headers={"X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 409
    with c.session_transaction() as sess:
        assert sess["cart"][str(product_id)] == 3

    response = c.post(f"/cart/remove/{product_id}", headers={"X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 200
    with c.session_transaction() as sess:
        assert str(product_id) not in sess.get("cart", {})


def test_empty_cart_checkout_does_not_create_order(client):
    c, _ = client
    response = c.post("/checkout", data={"fullname": "Test", "address": "Address", "phone": "0912345678"})
    assert response.status_code in (302, 303)
    with c.application.app_context():
        assert db.session.query(DonHang).count() == 0


def test_checkout_validation_rejects_blank_delivery_fields(client):
    c, product_id = client
    c.post(f"/cart/add/{product_id}", headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    response = c.post("/checkout", data={"fullname": "   ", "address": "Address", "phone": "0912345678"})
    assert response.status_code == 400
    with c.application.app_context():
        assert db.session.query(DonHang).count() == 0


def test_checkout_success_creates_order_detail_and_decrements_stock(client):
    c, product_id = client
    c.post(f"/cart/add/{product_id}", headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    with c.session_transaction() as sess:
        sess["cart"][str(product_id)] = 2
    response = c.post("/checkout", data={
        "fullname": "Nguyen Van A", "address": "123 Duong A", "phone": "0912345678"
    })
    assert response.status_code in (302, 303)
    with c.application.app_context():
        order = db.session.query(DonHang).one()
        detail = db.session.query(ChiTietDonHang).one()
        product = db.session.get(SanPham, product_id)
        assert order.MANGUOIDUNG is None
        assert float(order.TONGGIATRI) == 20000
        assert detail.SOLUONG == 2
        assert product.SOLUONGTON == 3
    with c.session_transaction() as sess:
        assert "cart" not in sess
        assert "last_order_id" in sess


def test_checkout_rejects_invalid_phone_without_order(client):
    c, product_id = client
    c.post(f"/cart/add/{product_id}", headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    response = c.post("/checkout", data={
        "fullname": "Nguyen Van A", "address": "123 Duong A", "phone": "abc"
    })
    assert response.status_code == 400
    with c.application.app_context():
        assert db.session.query(DonHang).count() == 0
        assert db.session.get(SanPham, product_id).SOLUONGTON == 5
    with c.session_transaction() as sess:
        assert sess["cart"][str(product_id)] == 1


@pytest.mark.parametrize("bad_quantity", [0, -1, "abc", 1.5])
def test_update_cart_rejects_invalid_quantity(client, bad_quantity):
    c, product_id = client
    c.post(f"/cart/add/{product_id}", headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    response = c.post(
        f"/cart/update/{product_id}", json={"quantity": bad_quantity},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert response.status_code == 400
    with c.session_transaction() as sess:
        assert sess["cart"][str(product_id)] == 1


def test_checkout_out_of_stock_keeps_cart_and_creates_no_order(client):
    c, product_id = client
    c.post(f"/cart/add/{product_id}", headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    with c.application.app_context():
        product = db.session.get(SanPham, product_id)
        product.SOLUONGTON = 0
        db.session.commit()
    response = c.post("/checkout", data={
        "fullname": "Nguyen Van A", "address": "123 Duong A", "phone": "0912345678"
    })
    assert response.status_code in (302, 303)
    with c.application.app_context():
        assert db.session.query(DonHang).count() == 0
    with c.session_transaction() as sess:
        assert sess["cart"][str(product_id)] == 1


def test_customer_order_is_not_accessible_through_guest_last_order_session(client):
    c, product_id = client
    with c.application.app_context():
        user = User(HOTEN="Customer", ROLE="customer")
        db.session.add(user)
        db.session.flush()
        order = DonHang(
            MANGUOIDUNG=user.MANGUOIDUNG, NGAYDAT=__import__("datetime").date.today(),
            TONGGIATRI=10000, TRANGTHAI=0, HOTENNHAN="Customer",
            DIACHIGIAO="Address", SDTNHAN="0912345678",
        )
        db.session.add(order)
        db.session.commit()
        order_id = order.MADONHANG
    with c.session_transaction() as sess:
        sess["last_order_id"] = order_id
    response = c.get(f"/order-success/{order_id}")
    assert response.status_code == 403


def test_checkout_database_failure_rolls_back_and_keeps_cart(client, monkeypatch):
    c, product_id = client
    c.post(f"/cart/add/{product_id}", headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    original_commit = db.session.commit

    def fail_commit():
        raise SQLAlchemyError("simulated database failure")

    monkeypatch.setattr(db.session, "commit", fail_commit)
    response = c.post("/checkout", data={
        "fullname": "Nguyen Van A", "address": "123 Duong A", "phone": "0912345678"
    })
    assert response.status_code == 500
    monkeypatch.setattr(db.session, "commit", original_commit)
    with c.application.app_context():
        assert db.session.query(DonHang).count() == 0
        assert db.session.get(SanPham, product_id).SOLUONGTON == 5
    with c.session_transaction() as sess:
        assert sess["cart"][str(product_id)] == 1
