from app.extensions import db


class DanhMuc(db.Model):
    __tablename__ = 'DANHMUC'
    MADANHMUC = db.Column(db.Integer, primary_key=True)
    TENDM = db.Column(db.Unicode(50))
    MADMCHA = db.Column(db.Integer, db.ForeignKey('DANHMUC.MADANHMUC'))
    con = db.relationship('DanhMuc', remote_side=[MADANHMUC])
