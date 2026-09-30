from app.extensions import db


class DonHang(db.Model):
    __tablename__ = 'DONHANG'
    MADONHANG = db.Column(db.Integer, primary_key=True)
    # Để trống (NULL) nếu khách đặt hàng khi chưa đăng nhập
    MANGUOIDUNG = db.Column(db.Integer, db.ForeignKey('NGUOIDUNG.MANGUOIDUNG'), nullable=True)
    NGAYDAT = db.Column(db.Date)
    TONGGIATRI = db.Column(db.Numeric(18, 2))
    TRANGTHAI = db.Column(db.Integer, default=0)

    # Thông tin giao hàng, lấy từ form checkout (fullname, address, phone)
    HOTENNHAN = db.Column(db.Unicode(200))
    DIACHIGIAO = db.Column(db.Unicode(300))
    SDTNHAN = db.Column(db.String(15))

    user = db.relationship('User', backref='donhang_list')