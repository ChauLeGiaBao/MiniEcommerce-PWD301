import os
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from app import create_app
from app.extensions import db
from app.models import SanPham, DonHang, ChiTietDonHang


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
