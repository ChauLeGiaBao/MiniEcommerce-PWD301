
from urllib.parse import urljoin, urlparse

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import auth_bp
from app.extensions import db
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


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Đăng ký tài khoản khách hàng mới (Customer).
    Sử dụng hash mật khẩu bảo mật và gán vai trò mặc định customer.
    Hỗ trợ chuyển hướng đến next_url an toàn (ví dụ: quay lại /checkout).
    """
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    next_url = request.args.get("next")

    if request.method == "POST":
        next_url = request.form.get("next") or request.args.get("next")
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Kiểm tra các trường bắt buộc
        if not full_name or not email or not password:
            flash("Vui lòng điền đầy đủ họ tên, email và mật khẩu.", "warning")
            return render_template(
                "register.html",
                full_name=full_name,
                email=email,
                phone=phone,
                next_url=next_url,
            ), 400

        # Kiểm tra định dạng email cơ bản
        if "@" not in email or "." not in email:
            flash("Địa chỉ email không hợp lệ.", "warning")
            return render_template(
                "register.html",
                full_name=full_name,
                email=email,
                phone=phone,
                next_url=next_url,
            ), 400

        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự.", "warning")
            return render_template(
                "register.html",
                full_name=full_name,
                email=email,
                phone=phone,
                next_url=next_url,
            ), 400

        # Kiểm tra xác nhận mật khẩu
        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp.", "warning")
            return render_template(
                "register.html",
                full_name=full_name,
                email=email,
                phone=phone,
                next_url=next_url,
            ), 400

        # Kiểm tra email trùng lặp
        existing_user = User.query.filter_by(EMAIL=email).first()
        if existing_user:
            flash("Email này đã được sử dụng. Vui lòng đăng nhập hoặc dùng email khác.", "danger")
            return render_template(
                "register.html",
                full_name=full_name,
                email=email,
                phone=phone,
                next_url=next_url,
            ), 400

        # Tạo tài khoản mới
        new_user = User(
            HOTEN=full_name,
            EMAIL=email,
            SDT=phone if phone else None,
            PASSWORD_HASH=generate_password_hash(password),
            ROLE="customer",
            TRANGTHAIND=1,
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Đã xảy ra lỗi trong quá trình đăng ký. Vui lòng thử lại sau.", "danger")
            return render_template(
                "register.html",
                full_name=full_name,
                email=email,
                phone=phone,
                next_url=next_url,
            ), 500

        # Tự động đăng nhập
        login_user(new_user)
        session.pop("last_order_id", None)
        flash(f"Đăng ký tài khoản thành công! Xin chào {new_user.HOTEN}.", "success")

        # Redirect về trang trước nếu URL an toàn (ví dụ: checkout)
        if next_url and is_safe_url(next_url):
            return redirect(next_url)

        return redirect(url_for("shop.products"))

    return render_template("register.html", full_name="", email="", phone="", next_url=next_url)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """
    Đổi mật khẩu tài khoản người dùng đã đăng nhập.
    Yêu cầu xác nhận mật khẩu hiện tại, kiểm tra độ dài mật khẩu mới
    và cập nhật mật khẩu băm Werkzeug vào cơ sở dữ liệu.
    """
    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not old_password or not new_password or not confirm_password:
            flash("Vui lòng điền đầy đủ tất cả các trường.", "warning")
            return render_template("change_password.html"), 400

        if not check_password_hash(current_user.PASSWORD_HASH or "", old_password):
            flash("Mật khẩu hiện tại không chính xác.", "danger")
            return render_template("change_password.html"), 400

        if len(new_password) < 6:
            flash("Mật khẩu mới phải có ít nhất 6 ký tự.", "warning")
            return render_template("change_password.html"), 400

        if new_password != confirm_password:
            flash("Xác nhận mật khẩu mới không khớp.", "warning")
            return render_template("change_password.html"), 400

        if old_password == new_password:
            flash("Mật khẩu mới không được trùng với mật khẩu cũ.", "warning")
            return render_template("change_password.html"), 400

        current_user.PASSWORD_HASH = generate_password_hash(new_password)
        try:
            db.session.commit()
            flash("Đổi mật khẩu thành công! Mật khẩu mới đã được cập nhật.", "success")
            return redirect(url_for("shop.products"))
        except Exception:
            db.session.rollback()
            flash("Đã xảy ra lỗi khi lưu mật khẩu. Vui lòng thử lại sau.", "danger")
            return render_template("change_password.html"), 500

    return render_template("change_password.html")


def generate_reset_token(email):
    """Tạo token đặt lại mật khẩu có chữ ký bảo mật và giới hạn thời gian (30 phút)."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="password-reset-salt")


def verify_reset_token(token, max_age=1800):
    """
    Xác thực token đặt lại mật khẩu.
    Trả về email nếu hợp lệ và chưa quá hạn (mặc định 1800 giây = 30 phút),
    ngược lại trả về None.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """
    Xử lý yêu cầu quên mật khẩu.
    Người dùng nhập email đăng ký; hệ thống sinh token bảo mật và tạo liên kết đặt lại mật khẩu.
    Tuân thủ nguyên tắc bảo mật: thông báo trung lập không làm lộ việc email có tồn tại hay không.
    Trong môi trường demo/dev, liên kết đặt lại mật khẩu được cung cấp trực tiếp trên giao diện.
    """
    if current_user.is_authenticated:
        return redirect(url_for("shop.products"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Vui lòng nhập địa chỉ email của bạn.", "warning")
            return render_template("forgot_password.html", email=email), 400

        user = User.query.filter_by(EMAIL=email).first()

        dev_reset_url = None
        if user and user.TRANGTHAIND == 1:
            token = generate_reset_token(user.EMAIL)
            dev_reset_url = url_for("auth.reset_password", token=token, _external=True)

        # Thông báo thành công chung (chống rò rỉ thông tin tài khoản)
        flash(
            "Nếu email tồn tại trong hệ thống, hướng dẫn đặt lại mật khẩu đã được khởi tạo thành công.",
            "info"
        )
        return render_template(
            "forgot_password.html",
            email_submitted=True,
            email=email,
            dev_reset_url=dev_reset_url
        )

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Xác thực token và cập nhật mật khẩu mới cho người dùng.
    Token có hạn sử dụng trong 30 phút.
    """
    if current_user.is_authenticated:
        return redirect(url_for("shop.products"))

    email = verify_reset_token(token)
    if not email:
        flash("Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn. Vui lòng gửi yêu cầu mới.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(EMAIL=email).first()
    if not user or user.TRANGTHAIND != 1:
        flash("Tài khoản không tồn tại hoặc đã bị vô hiệu hóa.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not new_password or not confirm_password:
            flash("Vui lòng nhập đầy đủ mật khẩu mới và xác nhận mật khẩu.", "warning")
            return render_template("reset_password.html", token=token), 400

        if len(new_password) < 6:
            flash("Mật khẩu mới phải có ít nhất 6 ký tự.", "warning")
            return render_template("reset_password.html", token=token), 400

        if new_password != confirm_password:
            flash("Xác nhận mật khẩu mới không khớp.", "warning")
            return render_template("reset_password.html", token=token), 400

        user.PASSWORD_HASH = generate_password_hash(new_password)
        try:
            db.session.commit()
            flash("Đặt lại mật khẩu thành công! Vui lòng đăng nhập với mật khẩu mới.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            flash("Đã xảy ra lỗi khi lưu mật khẩu. Vui lòng thử lại sau.", "danger")
            return render_template("reset_password.html", token=token), 500

    return render_template("reset_password.html", token=token)

