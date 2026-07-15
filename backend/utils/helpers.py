import re
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from backend.config import Config
from backend.db import db
from backend.models.models import StudentNotification

ALLOWED_EXTENSIONS = {'pdf'}
WEBSITE_REGEX = re.compile(getattr(Config, "WEBSITE_REGEX", r'^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(\/[\w.-]*)?/?$'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_resume_file(file_storage):
    """Validate and persist an uploaded resume file, returning its public
    URL path, or None if no file was provided. Raises ValueError with a
    user-facing message on invalid input."""
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Resume must be a PDF file.")

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{extension}"

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)
    file_storage.save(str(upload_folder / stored_name))

    return f"/uploads/resumes/{stored_name}"


def is_valid_website(value):
    if not value:
        return True
    return bool(WEBSITE_REGEX.fullmatch(value.strip()))


def create_student_notification(student_id, message, status='info', application_id=None):
    notification = StudentNotification(
        student_id=student_id,
        application_id=application_id,
        message=message,
        status=status
    )
    db.session.add(notification)
    return notification


def get_student_notifications(student_id, limit=None):
    query = StudentNotification.query.filter_by(student_id=student_id).order_by(
        StudentNotification.created_at.desc()
    )
    if limit:
        return query.limit(limit).all()
    return query.all()
