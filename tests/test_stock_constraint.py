import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import DanhMuc, SanPham


@pytest.fixture
def stock_app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        db.session.add(DanhMuc(MADANHMUC=11, TENDM="Phone"))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


def test_negative_stock_rejected(stock_app):
    db.session.add(SanPham(TENSPH="SP loi", DONGIA=1000, SOLUONGTON=-1,
                           TRANGTHAISPH=1, MADANHMUC=11))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_zero_stock_allowed(stock_app):
    db.session.add(SanPham(TENSPH="SP het hang", DONGIA=1000, SOLUONGTON=0,
                           TRANGTHAISPH=1, MADANHMUC=11))
    db.session.commit()
    assert SanPham.query.count() == 1