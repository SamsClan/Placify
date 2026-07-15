"""Student-facing API routes: dashboard, profile, job search/apply,
applications, notifications, and CSV export."""
from datetime import datetime, date
from pathlib import Path
from flask import Blueprint,current_app, jsonify, request, send_file, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import func, or_
from io import BytesIO
from celery.result import AsyncResult

from backend.db import db
from backend.utils.avatar_utils import generate_avatar_png
from backend.models.models import (
    Admin,
    ApprovalStatus,
    Application,
    ApplicationStatus,
    Company,
    DriveStatus,
    PlacementDrive,
    Placemment,
    Role,
    Student,
    StudentNotification,
)
from backend.extensions import cache
from backend.api.v1.common import (
    _current_user,
    _require_user,
    _cached_payload,
    _invalidate_cache,
    _serialize_drive,
    _serialize_application,
    _serialize_admin,
    _serialize_student,
    _serialize_company,
    _serialize_placement,
)
from backend.tasks.exports import export_student_applications, _export_dir
from backend.utils.helpers import save_resume_file, create_student_notification

student_bp = Blueprint("api_v1_student", __name__, url_prefix="/api/v1")



@student_bp.get("/dashboard/student")
@jwt_required()
def student_dashboard():
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    payload = _cached_payload(
        f"dashboard:student:{student.id}",
        lambda: {
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "department": student.department,
                "course": student.course,
                "year_of_study": student.year_of_study,
                "skills": student.skills,
                "resume_link": (request.url_root.rstrip('/') + student.resume_link) if student.resume_link and not student.resume_link.startswith(('http://','https://')) else student.resume_link,
            },
            "stats": {
                "recent_application_count": Application.query.filter_by(student_id=student.id).count(),
                "notification_count": StudentNotification.query.filter_by(student_id=student.id).count(),
            },
            "recent_applications": [
                {
                    "id": application.id,
                    "drive_id": application.drive_id,
                    "job_title": application.drive.job_title,
                    "company_name": application.drive.company.company_name,
                    "status": application.status.value,
                    "application_date": application.application_date.isoformat() if application.application_date else None,
                }
                for application in (
                    Application.query.filter_by(student_id=student.id)
                    .order_by(Application.application_date.desc())
                    .limit(5)
                    .all()
                )
            ],
            "notifications": [
                {
                    "id": notification.id,
                    "message": notification.message,
                    "status": notification.status,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                for notification in (
                    StudentNotification.query.filter_by(student_id=student.id)
                    .order_by(StudentNotification.created_at.desc())
                    .limit(5)
                    .all()
                )
            ],
        },
        timeout=60,
    )
    return jsonify(payload)


@student_bp.get("/student/profile")
@jwt_required()
def student_profile():
    student, error = _current_user(Role.STUDENT)
    if error:
        return error
    return jsonify(student=_serialize_student(student))


@student_bp.put("/student/profile")
@jwt_required()
def student_profile_update():
    student, error = _current_user(Role.STUDENT)
    if error:
        return error

    is_multipart = request.content_type and "multipart/form-data" in request.content_type
    data = request.form if is_multipart else (request.get_json(silent=True) or {})

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    department = (data.get("department") or "").strip()
    course = (data.get("course") or "").strip()
    year_of_study = data.get("year_of_study")
    bio = (data.get("bio") or "").strip()
    skills = (data.get("skills") or "").strip()
    resume_link = (data.get("resume_link") or "").strip()

    if is_multipart and request.files.get("resume"):
        try:
            resume_file_url = save_resume_file(request.files.get("resume"))
        except ValueError as exc:
            return jsonify(message=str(exc)), 400
        if resume_file_url:
            resume_link = resume_file_url

    if not name or len(name) < 2 or len(name) > 100:
        return jsonify(message="Invalid name."), 400
    if not email or "@" not in email:
        return jsonify(message="Invalid email address."), 400
    existing = Student.query.filter_by(email=email).first()
    if existing and existing.id != student.id:
        return jsonify(message="This email is already registered."), 409
    if not phone or len(phone) < 10:
        return jsonify(message="Invalid phone number."), 400
    if department and len(department) > 50:
        return jsonify(message="Department name cannot exceed 50 characters."), 400
    if course and len(course) > 50:
        return jsonify(message="Course name cannot exceed 50 characters."), 400
    if year_of_study is not None:
        try:
            year_value = int(year_of_study)
            if year_value < 1 or year_value > 4:
                return jsonify(message="Year of study must be between 1 and 4."), 400
        except (TypeError, ValueError):
            return jsonify(message="Year of study must be a valid number."), 400
    else:
        year_value = student.year_of_study
    if bio and len(bio) > 500:
        return jsonify(message="Bio cannot exceed 500 characters."), 400
    if skills and len(skills) > 200:
        return jsonify(message="Skills cannot exceed 200 characters."), 400
    if resume_link and len(resume_link) > 200:
        return jsonify(message="Resume URL cannot exceed 200 characters."), 400

    student.name = name
    student.email = email
    student.phone = phone
    student.department = department or None
    student.course = course or None
    student.year_of_study = year_value
    student.bio = bio or None
    student.skills = skills or None
    student.resume_link = resume_link or student.resume_link
    db.session.commit()
    _invalidate_cache(f"dashboard:student:{student.id}")
    return jsonify(message="Profile updated successfully.", student=_serialize_student(student))


@student_bp.get("/student/notifications")
@jwt_required()
def student_notifications():
    student, error = _current_user(Role.STUDENT)
    if error:
        return error

    notifications = StudentNotification.query.filter_by(student_id=student.id).order_by(
        StudentNotification.created_at.desc()
    ).all()

    return jsonify(
        notifications=[
            {
                "id": notification.id,
                "message": notification.message,
                "status": notification.status,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "application_id": notification.application_id,
            }
            for notification in notifications
        ]
    )


@student_bp.post("/student/notifications/clear")
@jwt_required()
def clear_student_notifications():
    student, error = _current_user(Role.STUDENT)
    if error:
        return error

    StudentNotification.query.filter_by(student_id=student.id).delete(synchronize_session=False)
    db.session.commit()
    return jsonify(message="All notifications cleared.")


@student_bp.get("/student/jobs")
@jwt_required()
def student_jobs():
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    drives = (
        PlacementDrive.query
        .join(Company)
        .filter(
            Company.approval_status == ApprovalStatus.APPROVED,
            PlacementDrive.approval_status == ApprovalStatus.APPROVED,
        )
        .order_by(PlacementDrive.drive_start_date.desc())
        .all()
    )

    applied_drive_ids = {
        application.drive_id
        for application in Application.query.filter_by(student_id=student.id).all()
    }

    return jsonify(
        drives=[
            _serialize_drive(
                drive,
                applied=drive.id in applied_drive_ids,
            )
            for drive in drives
        ]
    )


@student_bp.get("/student/jobs/<int:drive_id>")
@jwt_required()
def student_job_detail(drive_id):
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    drive = PlacementDrive.query.get_or_404(drive_id)

    if (
        drive.approval_status != ApprovalStatus.APPROVED
        or drive.company.approval_status != ApprovalStatus.APPROVED
    ):
        return jsonify(message="This job posting is not available."), 403

    existing_app = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive.id
    ).first()

    return jsonify(
        drive=_serialize_drive(drive, applied=existing_app is not None),
        has_applied=existing_app is not None,
        application=_serialize_application(existing_app) if existing_app else None,
    )

@student_bp.post("/student/jobs/<int:drive_id>/apply")
@jwt_required()
def student_apply(drive_id):
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.approval_status != ApprovalStatus.APPROVED or drive.company.approval_status != ApprovalStatus.APPROVED:
        return jsonify(message="This job posting is not available for applications."), 403
    if drive.status not in [DriveStatus.ONGOING, DriveStatus.UPCOMING]:
        return jsonify(message="This job posting is not accepting applications."), 400

    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing_app:
        return jsonify(message="You have already applied to this job."), 409

    if not request.content_type or "multipart/form-data" not in request.content_type:
        return jsonify(message="Please upload a PDF resume and cover letter."), 400

    data = request.form
    cover_letter = (data.get("cover_letter") or "").strip()
    resume_file = request.files.get("resume")

    if not resume_file:
        return jsonify(message="Please upload a PDF resume from your device."), 400

    try:
        resume_link = save_resume_file(resume_file)
    except ValueError as exc:
        return jsonify(message=str(exc)), 400

    if not cover_letter or len(cover_letter) > 1000:
        return jsonify(message="Cover letter is required and must be 1000 characters or less."), 400

    application = Application(
        student_id=student.id,
        drive_id=drive.id,
        cover_letter=cover_letter,
        resume_link=resume_link,
        status=ApplicationStatus.APPLIED,
    )
    db.session.add(application)
    db.session.commit()
    _invalidate_cache(
        f"dashboard:student:{student.id}",
        f"dashboard:company:{drive.company_id}",
        "dashboard:admin:*",
        "admin:charts:*",
    )

    return jsonify(message="Application submitted successfully.", application=_serialize_application(application)), 201


@student_bp.get("/student/applications")
@jwt_required()
def student_applications():
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    applications = (
        Application.query.filter_by(student_id=student.id)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .join(Company, PlacementDrive.company_id == Company.id)
        .order_by(Application.application_date.desc())
        .all()
    )

    return jsonify(applications=[_serialize_application(application) for application in applications])


@student_bp.post("/student/export-applications")
@jwt_required()
def student_export_applications():
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    celery_app = current_app.extensions.get("celery")
    broker_url = current_app.config.get("CELERY_BROKER_URL") or current_app.config.get("REDIS_URL")
    result_backend = current_app.config.get("CELERY_RESULT_BACKEND") or current_app.config.get("REDIS_URL")
    if celery_app is not None:
        celery_app.conf.broker_url = broker_url
        celery_app.conf.result_backend = result_backend
    export_student_applications.app.conf.broker_url = broker_url
    export_student_applications.app.conf.result_backend = result_backend
    export_student_applications.app = celery_app
    current_app.logger.info(
        "Queueing student export task for student=%s broker=%s task_app=%s",
        student.id,
        broker_url,
        getattr(export_student_applications.app, "main", None),
    )
    try:
        task = export_student_applications.delay(student.id, student.name, student.email)
    except Exception as exc:
        current_app.logger.exception("Failed to queue student export task")
        return jsonify(
            message="Failed to queue export task.",
            error=str(exc),
        ), 503

    return jsonify(message="Export started.", task_id=task.id, status="Pending")


@student_bp.get("/student/export-status/<task_id>")
@jwt_required()
def student_export_status(task_id):
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    result = AsyncResult(task_id, app=current_app.extensions["celery"])
    state = result.state
    if state in {"PENDING", "RETRY"}:
        status = "Pending"
    elif state in {"STARTED", "RECEIVED"}:
        status = "Processing"
    elif state == "SUCCESS":
        status = "Completed"
    else:
        status = "Failed"

    payload = {"task_id": task_id, "status": status}
    if state == "SUCCESS" and isinstance(result.result, dict):
        filename = result.result.get("filename")
        if filename:
            payload["download_url"] = url_for("api_v1_student.download_student_export", filename=filename)
    elif state == "FAILURE":
        payload["error"] = str(result.result)

    return jsonify(payload)


@student_bp.get("/student/exports/<path:filename>")
@jwt_required()
def download_student_export(filename):
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    export_root = _export_dir()
    export_path = export_root / filename
    if not export_path.exists() or not filename.startswith(f"student_{student.id}_"):
        return jsonify(message="Export not found."), 404

    return send_file(export_path, as_attachment=True, download_name=filename, mimetype="text/csv")


@student_bp.get("/student/applications/<int:application_id>")
@jwt_required()
def student_application_detail(application_id):
    identity = get_jwt_identity()
    student, error = _require_user(identity, Role.STUDENT)
    if error:
        return error

    application = Application.query.get_or_404(application_id)
    if application.student_id != student.id:
        return jsonify(message="You are not the owner of this application."), 403

    return jsonify(application=_serialize_application(application))
