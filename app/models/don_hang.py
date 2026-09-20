from app.extensions import db


class DonHang(db.Model):
    __tablename__ = 'DONHANG'
    MADONHANG = db.Column(db.Integer, primary_key=True)
    MANGUOIDUNG = db.Column(db.Integer, db.ForeignKey('NGUOIDUNG.MANGUOIDUNG'))
    NGAYDAT = db.Column(db.Date)
    TONGGIATRI = db.Column(db.Numeric(18, 2))
    TRANGTHAI = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='donhang_list')
