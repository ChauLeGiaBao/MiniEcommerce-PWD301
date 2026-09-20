from app.extensions import db


class User(db.Model):
    __tablename__ = 'NGUOIDUNG'
    MANGUOIDUNG = db.Column(db.Integer, primary_key=True)
    HOTEN = db.Column(db.Unicode(200))
    EMAIL = db.Column(db.String(200))
    SDT = db.Column(db.String(10))
    NGAYSINH = db.Column(db.Date)
    PASSWORD_HASH = db.Column(db.String(255))
    ROLE = db.Column(db.String(20), default='customer')
    TRANGTHAIND = db.Column(db.Integer, default=1)
