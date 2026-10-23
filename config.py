
import os
from datetime import timedelta

from dotenv import load_dotenv


# Read environment variables from .env.
# Existing system environment variables take priority.
load_dotenv()


class Config:
    # Flask session security
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-only-change-this-secret-key-before-deployment"
    )

    # Database configuration
    # SQLite is used for local development by default.
    # Docker can override DATABASE_URL to use SQL Server.
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL") or "sqlite:///dev.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # JWT Authentication
    JWT_SECRET_KEY = (
        os.getenv("JWT_SECRET_KEY") or SECRET_KEY
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

    JWT_TOKEN_LOCATION = ["headers"]

    # CSRF Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Session cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Set SESSION_COOKIE_SECURE=1 when using HTTPS.
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    )

    # Maximum request body: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
