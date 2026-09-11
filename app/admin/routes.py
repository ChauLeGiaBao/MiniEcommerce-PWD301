from flask import render_template
from app.admin import admin_bp


@admin_bp.route("/")
def dashboard():
    return render_template("admin_dashboard.html")