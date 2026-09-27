from app.extensions import db


class SanPham(db.Model):
    __tablename__ = 'SANPHAM'
    MASANPHAM = db.Column(db.Integer, primary_key=True)
    TENSPH = db.Column(db.Unicode(200))
    HINHANH = db.Column(db.String(500))
    DONGIA = db.Column(db.Numeric(18, 2))
    MOTA = db.Column(db.Unicode(500))
    SOLUONGTON = db.Column(db.Integer, default=0)
    TRANGTHAISPH = db.Column(db.Integer, default=1)
    MADANHMUC = db.Column(db.Integer, db.ForeignKey('DANHMUC.MADANHMUC'))
    danhmuc = db.relationship('DanhMuc', backref='sanpham_list')
