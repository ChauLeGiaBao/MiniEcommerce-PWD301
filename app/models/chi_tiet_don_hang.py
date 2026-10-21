from app.extensions import db


class ChiTietDonHang(db.Model):
    __tablename__ = 'CHITIETDONHANG'
    MADONHANG = db.Column(db.Integer, db.ForeignKey('DONHANG.MADONHANG'), primary_key=True)
    MASANPHAM = db.Column(db.Integer, db.ForeignKey('SANPHAM.MASANPHAM'), primary_key=True)
    SOLUONG = db.Column(db.Integer)
    donhang = db.relationship('DonHang', backref='chitiet_list')
    sanpham = db.relationship('SanPham')
