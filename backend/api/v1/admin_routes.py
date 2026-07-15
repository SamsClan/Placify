"""Admin-facing API routes: dashboard, analytics charts, background-job
triggers, and moderation of companies/students/drives/applications."""
from datetime import datetime, date
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, send_file, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import func, or_
from io import BytesIO
from celery.result import AsyncResult
from kombu.exceptions import OperationalError

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
from backend.tasks.reminders import send_daily_deadline_reminders
from backend.tasks.reports import generate_monthly_activity_report
from backend.utils import charts
from backend.utils.helpers import create_student_notification

admin_bp = Blueprint("api_v1_admin", __name__, url_prefix="/api/v1")



@admin_bp.get("/dashboard/admin")
@jwt_required()
def admin_dashboard():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_placement_drives = PlacementDrive.query.count()
    total_job_applications = Application.query.count()
    pending_companies = Company.query.filter_by(approval_status=ApprovalStatus.PENDING).count()
    approved_companies = Company.query.filter_by(approval_status=ApprovalStatus.APPROVED).count()
    active_students = Student.query.filter_by(is_blacklisted=False).count()
    total_placements = Placemment.query.count()
    ongoing_drives_count = PlacementDrive.query.filter(
        PlacementDrive.deadline >= func.current_date()
    ).count()

    payload = _cached_payload(
        f"dashboard:admin:{admin.id}",
        lambda: {
            "admin": {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "role": admin.role.name,
            },
            "stats": {
                "total_students": total_students,
                "total_companies": total_companies,
                "total_placement_drives": total_placement_drives,
                "total_job_applications": total_job_applications,
                "pending_companies": pending_companies,
                "approved_companies": approved_companies,
                "active_students": active_students,
                "total_placements": total_placements,
                "ongoing_drives_count": ongoing_drives_count,
            },
            "recent_applications": [
                {
                    "id": application.id,
                    "student_name": application.student.name,
                    "company_name": application.drive.company.company_name,
                    "job_title": application.drive.job_title,
                    "status": application.status.value,
                    "application_date": application.application_date.isoformat() if application.application_date else None,
                }
                for application in (
                    Application.query.order_by(Application.application_date.desc()).limit(15).all()
                )
            ],
        },
        timeout=60,
    )
    return jsonify(payload)


@admin_bp.get("/admin/charts")
@jwt_required()
def admin_charts():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    def _build_charts():
        # Applications by status
        status_counts = {
            "Applied": Application.query.filter_by(status=ApplicationStatus.APPLIED).count(),
            "Shortlisted": Application.query.filter_by(status=ApplicationStatus.SHORTLISTED).count(),
            "Selected": Application.query.filter_by(status=ApplicationStatus.SELECTED).count(),
            "Rejected": Application.query.filter_by(status=ApplicationStatus.REJECTED).count(),
        }

        # Drives by status (including pending approval, which sits outside DriveStatus)
        # Exclude drives that are still pending approval from the "Upcoming" bucket
        drive_counts = {
            "Pending": PlacementDrive.query.filter_by(approval_status=ApprovalStatus.PENDING).count(),
            "Upcoming": (
                PlacementDrive.query.filter_by(status=DriveStatus.UPCOMING)
                .filter(PlacementDrive.approval_status != ApprovalStatus.PENDING)
                .count()
            ),
            "Ongoing": PlacementDrive.query.filter_by(status=DriveStatus.ONGOING).count(),
            "Completed": PlacementDrive.query.filter_by(status=DriveStatus.COMPLETED).count(),
        }

        # Monthly trend for the last 6 months
        today = date.today()
        month_labels = []
        application_counts = []
        selected_counts = []
        for offset in range(5, -1, -1):
            month_index = today.month - offset
            year = today.year
            while month_index <= 0:
                month_index += 12
                year -= 1
            month_start = date(year, month_index, 1)
            next_month = month_index + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1
            month_end = date(next_year, next_month, 1)

            month_apps = Application.query.filter(
                Application.application_date >= month_start,
                Application.application_date < month_end,
            )
            month_labels.append(month_start.strftime("%b %Y"))
            application_counts.append(month_apps.count())
            selected_counts.append(month_apps.filter(Application.status == ApplicationStatus.SELECTED).count())

        # Top 5 recruiting companies by application count
        top_companies_query = (
            db.session.query(Company.company_name, func.count(Application.id).label("application_count"))
            .join(PlacementDrive, PlacementDrive.company_id == Company.id)
            .join(Application, Application.drive_id == PlacementDrive.id)
            .group_by(Company.id)
            .order_by(func.count(Application.id).desc())
            .limit(5)
            .all()
        )

        # Applications by student department
        department_counts = {}
        department_rows = (
            db.session.query(Student.department, func.count(Application.id))
            .join(Application, Application.student_id == Student.id)
            .filter(Student.department.isnot(None))
            .group_by(Student.department)
            .order_by(func.count(Application.id).desc())
            .limit(8)
            .all()
        )
        for department, count in department_rows:
            department_counts[department] = count

        return {
            "applications_by_status": charts.applications_by_status_chart(status_counts),
            "drives_by_status": charts.drives_by_status_chart(drive_counts),
            "monthly_trend": charts.monthly_trend_chart(month_labels, application_counts, selected_counts),
            "top_companies": charts.top_companies_chart(list(top_companies_query)),
            "department_distribution": charts.department_distribution_chart(department_counts),
            "generated_at": datetime.utcnow().isoformat(),
        }

    payload = _cached_payload(f"admin:charts:{admin.id}", _build_charts, timeout=120)
    return jsonify(payload)


@admin_bp.post("/admin/trigger-reminders")
@jwt_required()
def admin_trigger_reminders():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    celery_app = current_app.extensions["celery"]
    broker_url = current_app.config.get("CELERY_BROKER_URL") or current_app.config.get("REDIS_URL")
    result_backend = current_app.config.get("CELERY_RESULT_BACKEND") or current_app.config.get("REDIS_URL")

    celery_app.conf.broker_url = broker_url
    celery_app.conf.result_backend = result_backend
    send_daily_deadline_reminders.app.conf.broker_url = broker_url
    send_daily_deadline_reminders.app.conf.result_backend = result_backend
    send_daily_deadline_reminders.app = celery_app

    current_app.logger.info(
        "Queueing reminder task broker=%s task_app=%s",
        getattr(current_app.extensions.get("celery").conf, "broker_url", None),
        getattr(send_daily_deadline_reminders.app, "main", None),
    )
    try:
        task = send_daily_deadline_reminders.delay()
    except Exception as exc:
        current_app.logger.exception("Failed to queue reminder task")
        return jsonify(
            message="Failed to queue reminder task.",
            error=str(exc),
        ), 503

    return jsonify(message="Deadline reminders queued.", task_id=task.id, status="Pending")


@admin_bp.post("/admin/trigger-report")
@jwt_required()
def admin_trigger_report():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    celery_app = current_app.extensions["celery"]
    broker_url = current_app.config.get("CELERY_BROKER_URL") or current_app.config.get("REDIS_URL")
    result_backend = current_app.config.get("CELERY_RESULT_BACKEND") or current_app.config.get("REDIS_URL")

    celery_app.conf.broker_url = broker_url
    celery_app.conf.result_backend = result_backend
    generate_monthly_activity_report.app.conf.broker_url = broker_url
    generate_monthly_activity_report.app.conf.result_backend = result_backend
    generate_monthly_activity_report.app = celery_app

    current_app.logger.info(
        "Queueing monthly report task broker=%s task_app=%s",
        getattr(current_app.extensions.get("celery").conf, "broker_url", None),
        getattr(generate_monthly_activity_report.app, "main", None),
    )
    try:
        task = generate_monthly_activity_report.delay()
    except Exception as exc:
        current_app.logger.exception("Failed to queue monthly report task")
        return jsonify(
            message="Failed to queue monthly report task.",
            error=str(exc),
        ), 503

    return jsonify(message="Monthly report generation queued.", task_id=task.id, status="Pending")


@admin_bp.get("/admin/task-status/<task_id>")
@jwt_required()
def admin_task_status(task_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
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
        payload["result"] = {
            key: value
            for key, value in result.result.items()
            if key in {"status", "message", "notified_count", "drive_count", "failures"}
        }
    elif state == "FAILURE":
        payload["error"] = str(result.result)

    return jsonify(payload)


@admin_bp.get("/admin/companies")
@jwt_required()
def admin_manage_companies():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    query = (request.args.get("q") or "").strip()
    company_query = Company.query
    if query:
        company_query = company_query.filter(
            or_(
                Company.company_name.ilike(f"%{query}%"),
                Company.email.ilike(f"%{query}%"),
                Company.phone.ilike(f"%{query}%"),
                Company.website.ilike(f"%{query}%"),
                Company.hr_contact.ilike(f"%{query}%"),
            )
        )

    return jsonify(
        admin=_serialize_admin(admin),
        pending=[_serialize_company(company) for company in company_query.filter_by(approval_status=ApprovalStatus.PENDING).all()],
        approved=[_serialize_company(company) for company in company_query.filter_by(approval_status=ApprovalStatus.APPROVED).all()],
        blacklisted=[_serialize_company(company) for company in company_query.filter_by(approval_status=ApprovalStatus.BLACKLISTED).all()],
    )


@admin_bp.post("/admin/companies/<int:company_id>/approve")
@jwt_required()
def admin_approve_company(company_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    company = Company.query.get_or_404(company_id)
    company.approval_status = ApprovalStatus.APPROVED
    db.session.commit()
    _invalidate_cache(f"dashboard:company:{company.id}", "dashboard:admin:*", "admin:charts:*", "search:*")
    return jsonify(message="Company approved successfully.", company=_serialize_company(company))


@admin_bp.post("/admin/companies/<int:company_id>/blacklist")
@jwt_required()
def admin_blacklist_company(company_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    company = Company.query.get_or_404(company_id)
    company.approval_status = ApprovalStatus.BLACKLISTED
    db.session.commit()
    _invalidate_cache(f"dashboard:company:{company.id}", "dashboard:admin:*", "admin:charts:*", "search:*")
    return jsonify(message="Company blacklisted successfully.", company=_serialize_company(company))


@admin_bp.post("/admin/companies/<int:company_id>/unblacklist")
@jwt_required()
def admin_unblacklist_company(company_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    company = Company.query.get_or_404(company_id)
    company.approval_status = ApprovalStatus.APPROVED
    db.session.commit()
    _invalidate_cache(f"dashboard:company:{company.id}", "dashboard:admin:*", "admin:charts:*", "search:*")
    return jsonify(message="Company unblacklisted successfully.", company=_serialize_company(company))


@admin_bp.get("/admin/companies/<int:company_id>")
@jwt_required()
def admin_view_company(company_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    company = Company.query.get_or_404(company_id)
    return jsonify(company=_serialize_company(company))


@admin_bp.get("/admin/students")
@jwt_required()
def admin_manage_students():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    query = (request.args.get("q") or "").strip()
    active_query = Student.query.filter_by(is_blacklisted=False)
    blacklisted_query = Student.query.filter_by(is_blacklisted=True)

    if query:
        filter_condition = or_(
            Student.name.ilike(f"%{query}%"),
            Student.email.ilike(f"%{query}%"),
            Student.phone.ilike(f"%{query}%"),
            Student.enrollment_number.ilike(f"%{query}%"),
            Student.department.ilike(f"%{query}%"),
            Student.course.ilike(f"%{query}%"),
        )
        active_query = active_query.filter(filter_condition)
        blacklisted_query = blacklisted_query.filter(filter_condition)

    return jsonify(
        active=[_serialize_student(student) for student in active_query.all()],
        blacklisted=[_serialize_student(student) for student in blacklisted_query.all()],
    )


@admin_bp.get("/admin/students/<int:student_id>")
@jwt_required()
def admin_view_student(student_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    student = Student.query.get_or_404(student_id)
    return jsonify(student=_serialize_student(student))


@admin_bp.post("/admin/students/<int:student_id>/blacklist")
@jwt_required()
def admin_blacklist_student(student_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    _invalidate_cache(f"dashboard:student:{student.id}", "dashboard:admin:*", "admin:charts:*", "search:*")
    return jsonify(message="Student status updated successfully.", student=_serialize_student(student))


# @admin_bp.post("/admin/students/<int:student_id>/approve")
# @jwt_required()
# def admin_approve_student(student_id):
#     identity = get_jwt_identity()
#     admin, error = _require_user(identity, Role.ADMIN)
#     if error:
#         return error

#     student = Student.query.get_or_404(student_id)
#     student.is_blacklisted = False
#     db.session.commit()
#     _invalidate_cache(f"dashboard:student:{student.id}", "dashboard:admin:*", "admin:charts:*", "search:*")
#     return jsonify(message="Student approved successfully.", student=_serialize_student(student))


# @admin_bp.post("/admin/students/<int:student_id>/reject")
# @jwt_required()
# def admin_reject_student(student_id):
#     identity = get_jwt_identity()
#     admin, error = _require_user(identity, Role.ADMIN)
#     if error:
#         return error

#     student = Student.query.get_or_404(student_id)
#     db.session.delete(student)
#     db.session.commit()
#     _invalidate_cache(f"dashboard:student:{student_id}", "dashboard:admin:*", "admin:charts:*", "search:*")
#     return jsonify(message="Student rejected and removed successfully.")


@admin_bp.get("/admin/drives")
@jwt_required()
def admin_manage_placement_drives():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    return jsonify(
        upcoming=[_serialize_drive(drive) for drive in PlacementDrive.query.filter_by(status=DriveStatus.UPCOMING).all()],
        ongoing=[_serialize_drive(drive) for drive in PlacementDrive.query.filter_by(status=DriveStatus.ONGOING).all()],
        completed=[_serialize_drive(drive) for drive in PlacementDrive.query.filter_by(status=DriveStatus.COMPLETED).all()],
        pending=[_serialize_drive(drive) for drive in PlacementDrive.query.filter_by(approval_status=ApprovalStatus.PENDING).all()],
    )


@admin_bp.get("/admin/drives/<int:drive_id>")
@jwt_required()
def admin_view_placement_drive(drive_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    drive = PlacementDrive.query.get_or_404(drive_id)
    return jsonify(drive=_serialize_drive(drive))


@admin_bp.post("/admin/drives/<int:drive_id>/approve")
@jwt_required()
def admin_approve_drive(drive_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.approval_status = ApprovalStatus.APPROVED
    db.session.commit()
    _invalidate_cache(f"dashboard:company:{drive.company_id}", "dashboard:admin:*", "admin:charts:*", "search:*")
    return jsonify(message="Placement drive approved successfully.", drive=_serialize_drive(drive))


@admin_bp.post("/admin/drives/<int:drive_id>/reject")
@jwt_required()
def admin_reject_drive(drive_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    drive = PlacementDrive.query.get_or_404(drive_id)
    company_id = drive.company_id
    db.session.delete(drive)
    db.session.commit()
    _invalidate_cache(f"dashboard:company:{company_id}", "dashboard:admin:*", "admin:charts:*", "search:*")
    return jsonify(message="Placement drive rejected and removed successfully.")


@admin_bp.get("/admin/applications")
@jwt_required()
def admin_manage_applications():
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    return jsonify(
        applied=[_serialize_application(application) for application in Application.query.filter_by(status=ApplicationStatus.APPLIED).all()],
        shortlisted=[_serialize_application(application) for application in Application.query.filter_by(status=ApplicationStatus.SHORTLISTED).all()],
        selected=[_serialize_application(application) for application in Application.query.filter_by(status=ApplicationStatus.SELECTED).all()],
        rejected=[_serialize_application(application) for application in Application.query.filter_by(status=ApplicationStatus.REJECTED).all()],
    )


@admin_bp.get("/admin/applications/<int:application_id>")
@jwt_required()
def admin_view_application(application_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    application = Application.query.get_or_404(application_id)
    return jsonify(application=_serialize_application(application))




@admin_bp.post("/admin/applications/<int:application_id>/delete")
@jwt_required()
def admin_delete_application(application_id):
    identity = get_jwt_identity()
    admin, error = _require_user(identity, Role.ADMIN)
    if error:
        return error

    application = Application.query.get_or_404(application_id)
    student_id = application.student_id
    company_id = application.drive.company_id
    db.session.delete(application)
    db.session.commit()
    _invalidate_cache(f"dashboard:student:{student_id}", f"dashboard:company:{company_id}", "dashboard:admin:*", "admin:charts:*")
    return jsonify(message="Application deleted successfully.")
