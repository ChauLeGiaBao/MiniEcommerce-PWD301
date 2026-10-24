from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()


def create_or_update_user(
    email,
    password,
    full_name,
    role,
):
    user = User.query.filter_by(EMAIL=email).first()

    if user is None:
        user = User(
            HOTEN=full_name,
            EMAIL=email,
            PASSWORD_HASH=generate_password_hash(password),
            ROLE=role,
            TRANGTHAIND=1,
        )

        db.session.add(user)

        print(f"[CREATE] {email}")

    else:
        user.HOTEN = full_name
        user.PASSWORD_HASH = generate_password_hash(password)
        user.ROLE = role
        user.TRANGTHAIND = 1

        print(f"[UPDATE] {email}")


with app.app_context():

    create_or_update_user(
        email="admin@minishop.local",
        password="Admin@123",
        full_name="Mini Shop Admin",
        role="admin",
    )

    create_or_update_user(
        email="staff@minishop.local",
        password="Staff@123",
        full_name="Mini Shop Staff",
        role="staff",
    )

    create_or_update_user(
        email="customer@minishop.local",
        password="Customer@123",
        full_name="Test Customer",
        role="customer",
    )

    db.session.commit()

    print()
    print("=== TEST ACCOUNTS ===")
    print("ADMIN")
    print("Email: admin@minishop.local")
    print("Password: Admin@123")
    print()
    print("STAFF")
    print("Email: staff@minishop.local")
    print("Password: Staff@123")
    print()
    print("CUSTOMER")
    print("Email: customer@minishop.local")
    print("Password: Customer@123")