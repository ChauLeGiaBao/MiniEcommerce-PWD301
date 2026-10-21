from sqlalchemy import Float, cast, func
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import DanhGia

MAX_COMMENT_LEN = 1000


class ReviewError(Exception):
    """Lỗi nghiệp vụ khi gửi đánh giá (hiển thị trực tiếp cho người dùng)."""


def get_reviews(product_id):
    return (
        DanhGia.query.filter_by(MASANPHAM=product_id)
        .order_by(DanhGia.NGAYTAO.desc(), DanhGia.MADANHGIA.desc())
        .all()
    )


def get_rating_summary(product_id):
    avg, count = db.session.query(
        func.avg(cast(DanhGia.SOSAO, Float)), func.count(DanhGia.MADANHGIA)
    ).filter(DanhGia.MASANPHAM == product_id).one()
    return (round(float(avg), 1) if avg is not None else 0.0), count


def add_review(user_id, product_id, rating_raw, comment_raw):
    try:
        rating = int(rating_raw)
    except (TypeError, ValueError):
        raise ReviewError("Số sao phải là số nguyên từ 1 đến 5.")

    if not 1 <= rating <= 5:
        raise ReviewError("Số sao phải từ 1 đến 5.")

    comment = (comment_raw or "").strip()
    if len(comment) > MAX_COMMENT_LEN:
        raise ReviewError(f"Nhận xét tối đa {MAX_COMMENT_LEN} ký tự.")

    exists = DanhGia.query.filter_by(
        MANGUOIDUNG=user_id, MASANPHAM=product_id
    ).first()
    if exists:
        raise ReviewError("Bạn đã đánh giá sản phẩm này rồi.")

    review = DanhGia(
        MANGUOIDUNG=user_id,
        MASANPHAM=product_id,
        SOSAO=rating,
        NOIDUNG=comment or None,
    )
    db.session.add(review)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ReviewError("Không thể lưu đánh giá. Vui lòng thử lại.")
    return review