from datetime import datetime

from app.extensions import db


class DanhGia(db.Model):
    """Bảng liên kết User - Product (quan hệ M:N) kèm số sao và nhận xét."""
    __tablename__ = 'DANHGIA'

    MADANHGIA = db.Column(db.Integer, primary_key=True)
    MANGUOIDUNG = db.Column(
        db.Integer, db.ForeignKey('NGUOIDUNG.MANGUOIDUNG'), nullable=False
    )
    MASANPHAM = db.Column(
        db.Integer, db.ForeignKey('SANPHAM.MASANPHAM'), nullable=False
    )
    SOSAO = db.Column(db.Integer, nullable=False)
    NOIDUNG = db.Column(db.Unicode(1000))
    NGAYTAO = db.Column(db.DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        # Mỗi user chỉ đánh giá 1 lần cho mỗi sản phẩm
        db.UniqueConstraint('MANGUOIDUNG', 'MASANPHAM', name='UQ_DANHGIA_USER_SP'),
        db.CheckConstraint('SOSAO BETWEEN 1 AND 5', name='CK_DANHGIA_SOSAO'),
    )

    user = db.relationship('User', backref='danhgia_list')
    sanpham = db.relationship('SanPham', backref='danhgia_list')