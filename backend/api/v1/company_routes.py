"""Company-facing API routes: dashboard, profile, job postings, and
application/placement management."""
from datetime import datetime, date
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, send_file, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import func, or_
from io import BytesIO
from celery.result import AsyncResult
from backend.api.v1.common import _current_user
from backend.utils.helpers import create_student_notification, is_valid_website

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

company_bp = Blueprint("api_v1_company", __name__, url_prefix="/api/v1")



@company_bp.get("/dashboard/company")
@jwt_required()
def company_dashboard():
    identity = get_jwt_identity()
    company, error = _require_user(identity, Role.COMPANY)
    if error:
        return error

    payload = _cached_payload(
        f"dashboard:company:{company.id}",
        lambda: {
            "company": {
                "id": company.id,
                "name": company.name,
                "email": company.email,
                "company_name": company.company_name,
                "approval_status": company.approval_status.value,
                "website": company.website,
            },
            "stats": {
                "total_drives": PlacementDrive.query.filter_by(company_id=company.id).count(),
                "total_applications": Application.query.join(PlacementDrive).filter(
                    PlacementDrive.company_id == company.id
                ).count(),
                "active_drives": PlacementDrive.query.filter_by(company_id=company.id).filter(
                    PlacementDrive.status.in_([DriveStatus.UPCOMING, DriveStatus.ONGOING])
                ).count(),
                "shortlisted_count": Application.query.join(PlacementDrive).filter(
                    PlacementDrive.company_id == company.id,
                    Application.status == ApplicationStatus.SHORTLISTED,
                ).count(),
                "selected_count": Application.query.join(PlacementDrive).filter(
                    PlacementDrive.company_id == company.id,
                    Application.status == ApplicationStatus.SELECTED,
                ).count(),
            },
            "recent_applications": [
                {
                    "id": application.id,
                    "student_name": application.student.name,
                    "job_title": application.drive.job_title,
                    "status": application.status.value,
                    "application_date": application.application_date.isoformat() if application.application_date else None,
                }
                for application in (
                    Application.query.join(PlacementDrive)
                    .filter(PlacementDrive.company_id == company.id)
                    .order_by(Application.application_date.desc())
                    .limit(10)
                    .all()
                )
            ],
            "drives": [
                {
                    "id": drive.id,
                    "job_title": drive.job_title,
                    "status": drive.status.value,
                    "approval_status": drive.approval_status.value,
                    "deadline": drive.deadline.isoformat() if drive.deadline else None,
                }
                for drive in (
                    PlacementDrive.query.filter_by(company_id=company.id)
                    .order_by(PlacementDrive.drive_start_date.desc())
                    .limit(5)
                    .all()
                )
            ],
        },
        timeout=60,
    )
    return jsonify(payload)


@company_bp.get("/company/profile")
@jwt_required()
def company_profile():
    company, error = _current_user(Role.COMPANY)
    if error:
        return error
    return jsonify(company=_serialize_company(company))


@company_bp.put("/company/profile")
@jwt_required()
def company_profile_update():
    company, error = _current_user(Role.COMPANY)
    if error:
        return error

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    company_name = (data.get("company_name") or "").strip()
    bio = (data.get("bio") or "").strip()
    hr_contact = (data.get("hr_contact") or "").strip()
    website = (data.get("website") or "").strip()

    if not name or len(name) < 2 or len(name) > 100:
        return jsonify(message="Invalid name."), 400
    if not email or "@" not in email:
        return jsonify(message="Invalid email address."), 400
    existing = Company.query.filter_by(email=email).first()
    if existing and existing.id != company.id:
        return jsonify(message="This email is already registered."), 409
    if not phone or len(phone) < 10:
        return jsonify(message="Invalid phone number."), 400
    if not company_name or len(company_name) < 2 or len(company_name) > 150:
        return jsonify(message="Invalid company name."), 400
    existing_company = Company.query.filter_by(company_name=company_name).first()
    if existing_company and existing_company.id != company.id:
        return jsonify(message="This company name is already registered."), 409
    if website and not is_valid_website(website):
        return jsonify(message="Website URL must be a valid domain or full URL (for example, www.example.com or https://example.com)"), 400
    if bio and len(bio) > 500:
        return jsonify(message="Company bio cannot exceed 500 characters."), 400
    if hr_contact and len(hr_contact) > 100:
        return jsonify(message="HR contact name cannot exceed 100 characters."), 400

    company.name = name
    company.email = email
    company.phone = phone
    company.company_name = company_name
    company.bio = bio or None
    company.hr_contact = hr_contact or None
    company.website = website or None
    db.session.commit()
    _invalidate_cache(f"dashboard:company:{company.id}")
    return jsonify(message="Profile updated successfully.", company=_serialize_company(company))


@company_bp.post("/company/jobs")
@jwt_required()
def company_post_job():
    company, error = _current_user(Role.COMPANY)
    if error:
        return error

    data = request.get_json(silent=True) or {}
    job_title = (data.get("job_title") or "").strip()
    job_description = (data.get("job_description") or "").strip()
    eligibility_criteria = (data.get("eligibility_criteria") or "").strip()
    drive_start_date = (data.get("drive_start_date") or "").strip()
    deadline = (data.get("deadline") or "").strip()
    required_skills = (data.get("required_skills") or "").strip()
    experience_required = (data.get("experience_required") or "").strip()
    salary_range = (data.get("salary_range") or "").strip()

    if not job_title or len(job_title) < 3:
        return jsonify(message="Job title must be at least 3 characters."), 400
    if not job_description:
        return jsonify(message="Job description is required."), 400
    if not drive_start_date or not deadline:
        return jsonify(message="Start date and deadline are required."), 400

    try:
        start = datetime.strptime(drive_start_date, "%Y-%m-%d")
        end = datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        return jsonify(message="Invalid date format."), 400

    if start >= end:
        return jsonify(message="Deadline must be after start date."), 400

    drive = PlacementDrive(
        company_id=company.id,
        job_title=job_title,
        job_description=job_description,
        eligibility_criteria=eligibility_criteria,
        drive_start_date=start,
        deadline=end,
        status=DriveStatus.UPCOMING,
        approval_status=ApprovalStatus.PENDING,
        required_skills=required_skills or None,
        experience_required=experience_required or None,
        salary_range=salary_range or None,
    )

    if required_skills or experience_required or salary_range:
        drive.job_description += (
            f"\n\nRequired Skills: {required_skills or 'N/A'}"
            f"\nExperience: {experience_required or 'N/A'}"
            f"\nSalary Range: {salary_range or 'N/A'}"
        )

    db.session.add(drive)
    db.session.commit()
    _invalidate_cache(f"dashboard:company:{company.id}", "dashboard:admin:*", "admin:charts:*")
    return jsonify(message="Drive created successfully.", drive=_serialize_drive(drive)), 201


@company_bp.get("/company/jobs")
@jwt_required()
def company_manage_jobs():
    company, error = _current_user(Role.COMPANY)
    if error:
        return error

    query = (request.args.get("q") or "").strip()
    drives_query = PlacementDrive.query.filter_by(company_id=company.id)

    if query:
        drives_query = drives_query.filter(
            or_(
                PlacementDrive.job_title.ilike(f"%{query}%"),
                PlacementDrive.job_description.ilike(f"%{query}%"),
                PlacementDrive.eligibility_criteria.ilike(f"%{query}%"),
                PlacementDrive.required_skills.ilike(f"%{query}%"),
                PlacementDrive.experience_required.ilike(f"%{query}%"),
                PlacementDrive.salary_range.ilike(f"%{query}%"),
            )
        )

    drives = drives_query.order_by(PlacementDrive.drive_start_date.desc()).all()
    return jsonify(drives=[_serialize_drive(drive) for drive in drives])


@company_bp.post("/company/jobs/<int:drive_id>/status")
@jwt_required()
def company_update_job_status(drive_id):
    company, error = _current_user(Role.COMPANY)
    if error:
        return error

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return jsonify(message="Unauthorized."), 403
    if drive.approval_status != ApprovalStatus.APPROVED:
        return jsonify(message="Cannot update status of a drive that is not approved by admin."), 400

    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "").strip().lower()
    today = datetime.utcnow()

    if action == "active":
        new_deadline_str = (data.get("new_deadline") or "").strip()
        if not new_deadline_str:
            return jsonify(message="Please provide a new deadline to activate the drive."), 400
        try:
            new_deadline = datetime.strptime(new_deadline_str, "%Y-%m-%d")
        except ValueError:
            return jsonify(message="Invalid deadline format."), 400
        if new_deadline <= today:
            return jsonify(message="Deadline must be a future date."), 400
        drive.drive_start_date = today
        drive.deadline = new_deadline
        drive.status = DriveStatus.ONGOING
    elif action == "closed":
        drive.deadline = today
        drive.status = DriveStatus.COMPLETED
    elif action == "edit_dates":
        start_str = (data.get("new_start_date") or "").strip()
        deadline_str = (data.get("new_deadline_edit") or "").strip()
        if not start_str or not deadline_str:
            return jsonify(message="Start date and deadline are required."), 400
        try:
            new_start = datetime.strptime(start_str, "%Y-%m-%d")
            new_deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        except ValueError:
            return jsonify(message="Invalid date format."), 400
        if new_deadline <= new_start:
            return jsonify(message="Deadline must be after the start date."), 400
        drive.drive_start_date = new_start
        drive.deadline = new_deadline
        if today < new_start:
            drive.status = DriveStatus.UPCOMING
        elif today <= new_deadline:
            drive.status = DriveStatus.ONGOING
        else:
            drive.status = DriveStatus.COMPLETED
        drive.approval_status = ApprovalStatus.PENDING
    else:
        return jsonify(message="Invalid action."), 400

    db.session.commit()
    _invalidate_cache(f"dashboard:company:{company.id}", "dashboard:admin:*", "admin:charts:*")
    return jsonify(message="Drive status updated successfully.", drive=_serialize_drive(drive))


@company_bp.get("/company/applications")
@jwt_required()
def company_manage_applications():
    identity = get_jwt_identity()
    company, error = _require_user(identity, Role.COMPANY)
    if error:
        return error

    drive_filter = request.args.get('drive_id')
    query = Application.query.join(PlacementDrive).filter(PlacementDrive.company_id == company.id)
    if drive_filter:
        try:
            drive_id = int(drive_filter)
            query = query.filter(Application.drive_id == drive_id)
        except ValueError:
            return jsonify(message="Invalid drive_id."), 400
    applications = query.order_by(Application.application_date.desc()).all()
    return jsonify(applications=[_serialize_application(application) for application in applications])


@company_bp.post("/company/applications/<int:application_id>/status")
@jwt_required()
def company_update_application_status(application_id):
    identity = get_jwt_identity()
    company, error = _require_user(identity, Role.COMPANY)
    if error:
        return error

    app_obj = Application.query.get_or_404(application_id)
    if app_obj.drive.company_id != company.id:
        return jsonify(message="Unauthorized."), 403

    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip()
    remark = (data.get("remark") or "").strip()
    join_date_str = (data.get("join_date") or "").strip()
    join_date = None
    previous_status = app_obj.status
    previous_remark = (app_obj.remarks or "").strip()
    existing_placement = Placemment.query.filter_by(application_id=app_obj.id).first()
    previous_join_date = existing_placement.join_date if existing_placement else None

    if status == "Selected":
        if join_date_str:
            try:
                join_date = datetime.strptime(join_date_str, "%Y-%m-%d")
            except ValueError:
                return jsonify(message="Invalid join date format."), 400
        elif previous_join_date:
            join_date = previous_join_date
        else:
            return jsonify(message="Join date is required when marking a student as Selected."), 400

    if status in ["Selected", "Rejected"] and not remark:
        return jsonify(message="Remarks are required when marking a student as Selected or Rejected."), 400

    if remark:
        app_obj.remarks = remark
    if status in ["Shortlisted", "Selected", "Rejected"]:
        app_obj.status = ApplicationStatus[status.upper()]
    else:
        app_obj.status = ApplicationStatus.APPLIED

    if app_obj.status == ApplicationStatus.SELECTED:
        if not existing_placement:
            placement = Placemment(
                student_id=app_obj.student_id,
                company_id=app_obj.drive.company_id,
                drive_id=app_obj.drive_id,
                application_id=app_obj.id,
                join_date=join_date,
                package_lpa=app_obj.drive.salary_range,
            )
            db.session.add(placement)
        else:
            if join_date is not None:
                existing_placement.join_date = join_date
            existing_placement.package_lpa = app_obj.drive.salary_range
    else:
        if existing_placement:
            db.session.delete(existing_placement)

    if app_obj.status != previous_status and app_obj.status != ApplicationStatus.APPLIED:
        create_student_notification(
            student_id=app_obj.student_id,
            application_id=app_obj.id,
            status=app_obj.status.value,
            message=f"Your application for {app_obj.drive.job_title} at {app_obj.drive.company.company_name} has been updated to {app_obj.status.value.title()}.",
        )

    if remark and remark != previous_remark:
        create_student_notification(
            student_id=app_obj.student_id,
            application_id=app_obj.id,
            status=app_obj.status.value if app_obj.status != ApplicationStatus.APPLIED else "info",
            message=f"Remarks for your application for {app_obj.drive.job_title} were updated: {remark}",
        )

    if app_obj.status == ApplicationStatus.SELECTED and join_date and join_date != previous_join_date:
        create_student_notification(
            student_id=app_obj.student_id,
            application_id=app_obj.id,
            status=app_obj.status.value,
            message=f"Your joining date for {app_obj.drive.job_title} has been set to {join_date.strftime('%d %b %Y')}.",
        )

    db.session.commit()
    _invalidate_cache(
        f"dashboard:student:{app_obj.student_id}",
        f"dashboard:company:{company.id}",
        "dashboard:admin:*",
        "admin:charts:*",
    )
    return jsonify(message="Application status updated successfully.", application=_serialize_application(app_obj))


@company_bp.get("/company/selected-students")
@jwt_required()
def company_selected_students():
    identity = get_jwt_identity()
    company, error = _require_user(identity, Role.COMPANY)
    if error:
        return error

    drive_filter = request.args.get('drive_id')
    query = Placemment.query.filter_by(company_id=company.id)
    if drive_filter:
        try:
            drive_id = int(drive_filter)
            query = query.filter(Placemment.drive_id == drive_id)
        except ValueError:
            return jsonify(message="Invalid drive_id."), 400
    placements = query.all()
    return jsonify(selected=[_serialize_placement(placement) for placement in placements])


@company_bp.get("/company/shortlisted")
@jwt_required()
def company_view_shortlisted():
    identity = get_jwt_identity()
    company, error = _require_user(identity, Role.COMPANY)
    if error:
        return error

    drive_filter = request.args.get('drive_id')
    query = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id,
        Application.status == ApplicationStatus.SHORTLISTED,
    )
    if drive_filter:
        try:
            drive_id = int(drive_filter)
            query = query.filter(Application.drive_id == drive_id)
        except ValueError:
            return jsonify(message="Invalid drive_id."), 400
    shortlisted = query.all()
    return jsonify(shortlisted=[_serialize_application(application) for application in shortlisted])


@company_bp.get("/company/applications/<int:application_id>")
@jwt_required()
def company_view_application(application_id):
    identity = get_jwt_identity()
    company, error = _require_user(identity, Role.COMPANY)
    if error:
        return error

    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != company.id:
        return jsonify(message="Unauthorized."), 403

    return jsonify(application=_serialize_application(application))
