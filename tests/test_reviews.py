from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from app.extensions import db
from app.models import DanhGia, User
from app.services.review_service import (
    ReviewError, add_review, get_rating_summary,
)
from tests.conftest import seed_sample_data


@pytest.fixture
def review_app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        seed_sample_data()  # sản phẩm 1-5, sản phẩm 5 đang ẩn
        db.session.add_all([
            User(MANGUOIDUNG=1, HOTEN="Khach A", ROLE="customer"),
            User(MANGUOIDUNG=2, HOTEN="Khach B", ROLE="customer"),
        ])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def review_client(review_app):
    return review_app.test_client()


def fake_user(user_id=1, authenticated=True):
    u = MagicMock()
    u.is_authenticated = authenticated
    u.MANGUOIDUNG = user_id
    return u


CURRENT_USER = "app.shop.product_routes.current_user"


# ---------- Service ----------
def test_add_review_ok_and_average(review_app):
    add_review(1, 1, "5", "Rất tốt")
    add_review(2, 1, "3", "")
    avg, count = get_rating_summary(1)
    assert count == 2
    assert avg == 4.0


@pytest.mark.parametrize("bad", ["0", "6", "-1", "abc", "", None])
def test_rating_out_of_range_blocked(review_app, bad):
    with pytest.raises(ReviewError):
        add_review(1, 1, bad, "x")
    assert DanhGia.query.count() == 0


def test_duplicate_review_blocked(review_app):
    add_review(1, 1, "4", "ok")
    with pytest.raises(ReviewError):
        add_review(1, 1, "5", "lần 2")
    assert DanhGia.query.count() == 1


def test_comment_too_long_blocked(review_app):
    with pytest.raises(ReviewError):
        add_review(1, 1, "4", "a" * 1001)


# ---------- Route ----------
def test_guest_cannot_submit(review_client):
    with patch(CURRENT_USER, fake_user(authenticated=False)):
        res = review_client.post("/products/1/reviews", data={"rating": "5"})
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]
    assert DanhGia.query.count() == 0


def test_customer_can_submit(review_client):
    with patch(CURRENT_USER, fake_user(1)):
        res = review_client.post(
            "/products/1/reviews", data={"rating": "5", "comment": "Tuyệt"}
        )
    assert res.status_code == 302
    assert DanhGia.query.count() == 1


def test_route_rating_0_and_6_blocked(review_client):
    with patch(CURRENT_USER, fake_user(1)):
        review_client.post("/products/1/reviews", data={"rating": "0"})
        review_client.post("/products/1/reviews", data={"rating": "6"})
    assert DanhGia.query.count() == 0


def test_review_unknown_product_404(review_client):
    with patch(CURRENT_USER, fake_user(1)):
        res = review_client.post("/products/9999/reviews", data={"rating": "5"})
    assert res.status_code == 404


def test_review_hidden_product_404(review_client):
    with patch(CURRENT_USER, fake_user(1)):
        res = review_client.post("/products/5/reviews", data={"rating": "5"})
    assert res.status_code == 404
    assert DanhGia.query.count() == 0


# ---------- Giao diện ----------
def test_detail_shows_review(review_client):
    add_review(1, 1, "4", "Dùng ổn")
    page = review_client.get("/products/1").data.decode("utf-8")
    assert "Dùng ổn" in page
    assert "1 đánh giá" in page


def test_xss_comment_is_escaped(review_client):
    add_review(1, 1, "5", "<script>alert(1)</script>")
    page = review_client.get("/products/1").data.decode("utf-8")
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page