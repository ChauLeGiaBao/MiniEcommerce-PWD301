from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from app.auth import auth_bp
from app.models import User


def is_safe_url(target):
    """
    Chỉ cho phép redirect về URL cùng domain.
    Ngăn open redirect thông qua tham số ?next=
    """
    if not target:
        return False

    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))

    return (
        redirect_url.scheme in ("http", "https")
        and host_url.netloc == redirect_url.netloc
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Nếu đã đăng nhập thì không hiện login nữa
    if current_user.is_authenticated:
        role = (current_user.ROLE or "").strip().lower()

        if role == "admin":
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("shop.products"))

    next_url = request.args.get("next")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        next_url = request.form.get("next") or request.args.get("next")

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

        user = User.query.filter_by(EMAIL=email).first()

        if (
            user is None
            or not user.PASSWORD_HASH
            or not check_password_hash(user.PASSWORD_HASH, password)
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

        login_user(user)

        flash(
            f"Đăng nhập thành công. Xin chào {user.HOTEN}.",
            "success",
        )

        # Nếu user bị redirect từ một trang trước đó
        if next_url and is_safe_url(next_url):
            return redirect(next_url)

        role = (user.ROLE or "").strip().lower()

        if role == "admin":
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("shop.products"))

    return render_template(
        "login.html",
        email="",
        next_url=next_url,
    )


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Đã đăng xuất.", "success")

    return redirect(url_for("auth.login"))