
from urllib.parse import urljoin, urlparse

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash

from app.auth import auth_bp
from app.models import User


def is_safe_url(target):
    """
    Chi cho phep redirect ve URL cung domain.
    Ngan chan Open Redirect thong qua tham so next.
    """
    if not target:
        return False

    host_url = urlparse(request.host_url)
    redirect_url = urlparse(
        urljoin(request.host_url, target)
    )

    return (
        redirect_url.scheme in ("http", "https")
        and host_url.netloc == redirect_url.netloc
    )


def redirect_by_role(user):
    """
    Dieu huong nguoi dung theo role.

    Admin: Dashboard
    Staff: Dashboard
    Customer: Shop
    """
    role = (user.ROLE or "").strip().lower()

    if role in ("admin", "staff"):
        return redirect(url_for("admin.dashboard"))

    return redirect(url_for("shop.products"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login bang email va password.
    Su dung Flask-Login de quan ly session.
    """

    # Neu da login, khong hien lai form dang nhap
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    next_url = request.args.get("next")

    # Xu ly POST login
    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        next_url = (
            request.form.get("next")
            or request.args.get("next")
        )

        # Validate input
        if not email or not password:
            flash(
                "Vui lòng nhập đầy đủ email và mật khẩu.",
                "warning",
            )

            return render_template(
                "login.html",
                email=email,
                next_url=next_url,
            ), 400

        # Tim user trong database
        user = User.query.filter_by(
            EMAIL=email
        ).first()

        # Kiem tra password hash
        if (
            user is None
            or not user.PASSWORD_HASH
            or not check_password_hash(
                user.PASSWORD_HASH,
                password,
            )
        ):
            flash(
                "Email hoặc mật khẩu không đúng.",
                "danger",
            )

            return render_template(
                "login.html",
                email=email,
                next_url=next_url,
            ), 401

        # Kiem tra tai khoan con hoat dong
        if user.TRANGTHAIND != 1:
            flash(
                "Tài khoản đã bị vô hiệu hóa.",
                "danger",
            )

            return render_template(
                "login.html",
                email=email,
                next_url=next_url,
            ), 403

        # Xoa tham chieu don hang cu trong session
        session.pop("last_order_id", None)

        # Dang nhap bang Flask-Login
        login_user(user)

        flash(
            f"Đăng nhập thành công. Xin chào {user.HOTEN}.",
            "success",
        )

        # Redirect ve trang truoc neu URL an toan
        if next_url and is_safe_url(next_url):
            return redirect(next_url)

        # Khong co next hop le: redirect theo role
        return redirect_by_role(user)

    # Xu ly GET login
    return render_template(
        "login.html",
        email="",
        next_url=next_url,
    )


@auth_bp.post("/logout")
def logout():
    """
    Logout bang POST request.
    CSRFProtect kiem tra token truoc khi xu ly.
    """

    if current_user.is_authenticated:
        logout_user()

        # Xoa tham chieu don hang cua session cu
        session.pop("last_order_id", None)

        flash(
            "Đã đăng xuất.",
            "success",
        )

    return redirect(url_for("auth.login"))
