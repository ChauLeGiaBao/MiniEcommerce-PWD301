from flask import render_template
from app.auth import auth_bp


@auth_bp.route("/login")
def login():
    return render_template("login.html")