import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _normalize_db_url(url):
    # Render/Railway/Heroku hand out "postgres://" but SQLAlchemy 1.4+
    # requires the "postgresql://" scheme - swap it transparently.
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'studentprojecthub.db')}"
    ))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # pool_pre_ping avoids "server closed the connection unexpectedly" errors
    # that show up in production when a managed Postgres drops idle connections.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", 25)) * 1024 * 1024

    UPLOAD_ROOT = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {
        "pdf", "doc", "docx", "zip", "rar", "7z", "ppt", "pptx",
        "png", "jpg", "jpeg", "txt", "py", "java", "sql", "ipynb"
    }

    # S3-compatible object storage (AWS S3, Cloudflare R2, DigitalOcean Spaces...).
    # Leave S3_BUCKET unset to keep using local disk (fine for local dev only -
    # most hosting platforms wipe local disk on every deploy/restart).
    S3_BUCKET = os.environ.get("S3_BUCKET", "")
    S3_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID", "")
    S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY", "")
    S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", "")  # blank for AWS S3 itself
    S3_REGION = os.environ.get("S3_REGION", "auto")
    S3_PUBLIC_BASE_URL = os.environ.get("S3_PUBLIC_BASE_URL", "")  # for public avatar URLs

    RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@studentprojecthub.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "Site Admin")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
