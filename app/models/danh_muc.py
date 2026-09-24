from app.extensions import db


class DanhMuc(db.Model):
    __tablename__ = 'DANHMUC'
    MADANHMUC = db.Column(db.Integer, primary_key=True)
    TENDM = db.Column(db.Unicode(50))