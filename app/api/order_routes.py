
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api import api_bp
from app.extensions import db
from app.models import DonHang, User


VALID_STATUSES = {0, 1, 2, 3}
MANAGEMENT_ROLES = {"admin", "staff"}


def _jwt_user():
    """Always re-check the user and role against the database."""
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    user = db.session.get(User, user_id)

    if user is None or user.TRANGTHAIND != 1:
        return None

    return user


def _role(user):
    return (user.ROLE or "").strip().lower()


def _is_management(user):
    return _role(user) in MANAGEMENT_ROLES


def _positive_query_int(name, default, maximum=None):
    raw = request.args.get(name)

    if raw is None:
        return default

    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None

    if value < 1 or (maximum is not None and value > maximum):
        return None

    return value


def _order_to_dict(order, include_details=False):
    data = {
        "id": order.MADONHANG,
        "user_id": order.MANGUOIDUNG,
        "ordered_at": (
            order.NGAYDAT.isoformat()
            if order.NGAYDAT else None
        ),
        "total": (
            str(order.TONGGIATRI)
            if order.TONGGIATRI is not None else "0.00"
        ),
        "status": order.TRANGTHAI,
    }

    if include_details:
        data["recipient"] = {
            "name": order.HOTENNHAN,
            "address": order.DIACHIGIAO,
            "phone": order.SDTNHAN,
        }

        data["items"] = [
            {
                "product_id": item.MASANPHAM,
                "product_name": (
                    item.sanpham.TENSPH
                    if item.sanpham else None
                ),
                "quantity": item.SOLUONG,
            }
            for item in sorted(
                order.chitiet_list,
                key=lambda row: row.MASANPHAM
            )
        ]

    return data


@api_bp.get("/orders")
@jwt_required()
def api_orders():
    user = _jwt_user()

    if user is None:
        return jsonify({"error": "Invalid or inactive user"}), 401

    page = _positive_query_int("page", 1)
    per_page = _positive_query_int("per_page", 10, 50)

    if page is None or per_page is None:
        return jsonify({
            "error": "Invalid pagination parameters"
        }), 400

    query = DonHang.query

    if not _is_management(user):
        query = query.filter(
            DonHang.MANGUOIDUNG == user.MANGUOIDUNG
        )

    pagination = (
        query.order_by(DonHang.MADONHANG.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({
        "data": [
            _order_to_dict(order)
            for order in pagination.items
        ],
        "count": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }), 200


@api_bp.get("/orders/<int:order_id>")
@jwt_required()
def api_order_detail(order_id):
    user = _jwt_user()

    if user is None:
        return jsonify({"error": "Invalid or inactive user"}), 401

    order = db.session.get(DonHang, order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    if (
        not _is_management(user)
        and order.MANGUOIDUNG != user.MANGUOIDUNG
    ):
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(
        _order_to_dict(order, include_details=True)
    ), 200


@api_bp.put("/orders/<int:order_id>/status")
@jwt_required()
def api_update_order_status(order_id):
    user = _jwt_user()

    if user is None:
        return jsonify({"error": "Invalid or inactive user"}), 401

    if not _is_management(user):
        return jsonify({
            "error": "Admin or Staff permission required"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "JSON object is required"
        }), 400

    status = data.get("status")

    if type(status) is not int or status not in VALID_STATUSES:
        return jsonify({
            "error": "Status must be an integer from 0 to 3"
        }), 400

    order = db.session.get(DonHang, order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    order.TRANGTHAI = status
    db.session.commit()

    return jsonify({
        "message": "Order status updated successfully",
        "order": _order_to_dict(order),
    }), 200
