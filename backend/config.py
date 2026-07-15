import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'placement_portal.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 1800
    SESSION_REFRESH_EACH_REQUEST = True

    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = 30

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TASK_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")
    CELERY_ENABLE_UTC = True

    REMINDER_DAYS_AHEAD = int(os.getenv("REMINDER_DAYS_AHEAD", "30"))
    REMINDER_SCHEDULE_HOUR = int(os.getenv("REMINDER_SCHEDULE_HOUR", "9"))
    REMINDER_SCHEDULE_MINUTE = int(os.getenv("REMINDER_SCHEDULE_MINUTE", "0"))
    REMINDER_EMAIL_SUBJECT = os.getenv("REMINDER_EMAIL_SUBJECT", "Placement deadline reminder")
    MONTHLY_REPORT_SUBJECT = os.getenv("MONTHLY_REPORT_SUBJECT", "Monthly Activity Report")
    EXPORTS_DIR = os.getenv("EXPORTS_DIR", os.path.join(STORAGE_DIR, "exports"))
    EXPORT_RETENTION_HOURS = int(os.getenv("EXPORT_RETENTION_HOURS", "24"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))

    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")

    # Website URL validation regex - accepts full URLs or common domain forms like www.example.com
    WEBSITE_REGEX = r'^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(\/[\w.-]*)?/?$'


__all__ = ["Config"]
