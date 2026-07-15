"""
Shared helpers used across the admin/company/student route modules:
auth/role checks, serializers, caching helpers, plus the small set of
routes (cache debug, avatars, global search) that don't belong to any
single role.
"""
from datetime import datetime, date
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, send_file, url_for
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

common_bp = Blueprint("api_v1_common", __name__, url_prefix="/api/v1")



@common_bp.get("/cache")
def cache_debug():
    try:
        client = cache.cache._read_client
        cache_keys = client.keys("*")
    except Exception:
        cache_keys = []

    key_prefix = current_app.config.get("CACHE_KEY_PREFIX", "flask_cache_")
    entries = []
    for raw_key in cache_keys:
        try:
            decoded_key = raw_key.decode("utf-8") if isinstance(raw_key, bytes) else str(raw_key)
            # Flask-Caching adds this prefix internally, so it must be
            # stripped before calling cache.get() (which re-applies it).
            lookup_key = decoded_key[len(key_prefix):] if decoded_key.startswith(key_prefix) else decoded_key
            ttl = client.ttl(raw_key)
            entries.append({
                "key": lookup_key,
                "value": cache.get(lookup_key),
                "ttl_seconds": ttl if ttl is not None and ttl >= 0 else None,
            })
        except Exception:
            entries.append({"key": str(raw_key), "value": None, "ttl_seconds": None})

    return jsonify({"count": len(entries), "entries": entries})


def _load_user(identity):
    claims = get_jwt()
    if isinstance(identity, dict):
        user_id = identity.get("user_id")
        role = identity.get("role")
    else:
        user_id = identity
        role = claims.get("role")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        pass

    if role == Role.ADMIN.name:
        return Admin.query.get(user_id)
    if role == Role.COMPANY.name:
        return Company.query.get(user_id)
    if role == Role.STUDENT.name:
        return Student.query.get(user_id)
    return None


def _require_user(identity, expected_role):
    claims = get_jwt()
    role = identity.get("role") if isinstance(identity, dict) else claims.get("role")
    if role != expected_role.name:
        return None, (jsonify(message="Forbidden."), 403)

    user = _load_user(identity)
    if not user:
        return None, (jsonify(message="User not found."), 404)

    return user, None


def _current_user(expected_role):
    identity = get_jwt_identity()
    return _require_user(identity, expected_role)


def _cached_payload(key, payload_builder, timeout=60):
    cached_payload = cache.get(key)
    if cached_payload is not None:
        return cached_payload

    payload = payload_builder()
    cache.set(key, payload, timeout=timeout)
    return payload


def _invalidate_cache(*patterns):
    """Eagerly clear cached payloads matching any of the given glob patterns,
    so writes are reflected immediately instead of waiting for TTL expiry."""
    try:
        client = cache.cache._read_client
    except AttributeError:
        return
    # Flask-Caching prefixes every stored key (default: "flask_cache_"), so the
    # same prefix must be applied to the glob pattern used for lookup/deletion.
    key_prefix = current_app.config.get("CACHE_KEY_PREFIX", "flask_cache_")
    for pattern in patterns:
        try:
            keys = client.keys(f"{key_prefix}{pattern}")
        except Exception:
            continue
        if keys:
            client.delete(*keys)


def _serialize_drive(drive, applied=False):
    return {
        "id": drive.id,
        "company_id": drive.company_id,
        "company_name": drive.company.company_name,
        "company_email": drive.company.email,
        "job_title": drive.job_title,
        "job_description": drive.job_description,
        "eligibility_criteria": drive.eligibility_criteria,
        "salary_range": drive.salary_range,
        "required_skills": drive.required_skills,
        "experience_required": drive.experience_required,
        "status": drive.status.value,
        "approval_status": drive.approval_status.value,
        "drive_start_date": drive.drive_start_date.isoformat() if drive.drive_start_date else None,
        "deadline": drive.deadline.isoformat() if drive.deadline else None,
        "applied": applied,
    }


def _serialize_application(application):
    def _abs_url(path):
        if not path:
            return None
        if path.startswith("http://") or path.startswith("https://"):
            return path
        base = request.url_root.rstrip('/')
        return f"{base}{path if path.startswith('/') else '/' + path}"

    placement = application.placement                    # ← "placemment" → "placement"

    return {
        "id": application.id,
        "student_id": application.student_id,
        "drive_id": application.drive_id,
        "status": application.status.value,
        "remarks": application.remarks,
        "resume_link": _abs_url(application.resume_link),
        "cover_letter": application.cover_letter,
        "application_date": application.application_date.isoformat() if application.application_date else None,
        "join_date": placement.join_date.isoformat() if placement and placement.join_date else None,  # ← top-level, None-safe, isoformat
        "package_lpa": placement.package_lpa if placement else None,
        "student": {
            "id": application.student.id,
            "name": application.student.name,
            "email": application.student.email,
        },
        "company": {
            "id": application.drive.company.id,
            "name": application.drive.company.name,
            "company_name": application.drive.company.company_name,
        },
        "drive": {
            "id": application.drive.id,
            "job_title": application.drive.job_title,
            "status": application.drive.status.value,
            "approval_status": application.drive.approval_status.value,
        },
    }

def _serialize_admin(admin):
    return {
        "id": admin.id,
        "name": admin.name,
        "email": admin.email,
        "phone": admin.phone,
        "role": admin.role.name,
        "is_active": admin.is_active,
    }


def _serialize_student(student):
    def _abs_url(path):
        if not path:
            return None
        if path.startswith("http://") or path.startswith("https://"):
            return path
        base = request.url_root.rstrip('/') if request else current_app.config.get('BASE_URL', '')
        return f"{base}{path if path.startswith('/') else '/' + path}"

    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "bio": getattr(student, "bio", None),
        "enrollment_number": getattr(student, "enrollment_number", None),
        "department": getattr(student, "department", None),
        "course": getattr(student, "course", None),
        "skills": getattr(student, "skills", None),
        "resume_link": _abs_url(getattr(student, "resume_link", None)),
        "is_blacklisted": getattr(student, "is_blacklisted", False),
        "year_of_study": getattr(student, "year_of_study", None),
        "role": student.role.name,
    }


def _serialize_company(company):
    return {
        "id": company.id,
        "name": company.name,
        "email": company.email,
        "phone": company.phone,
        "bio": company.bio,
        "company_name": company.company_name,
        "hr_contact": company.hr_contact,
        "website": company.website,
        "approval_status": company.approval_status.value,
        "role": company.role.name,
    }


def _serialize_placement(placement):
    return {
        "id": placement.id,
        "student_id": placement.student_id,
        "student_name": placement.student.name,
        "company_id": placement.company_id,
        "company_name": placement.company.company_name,
        "drive_id": placement.drive_id,
        "job_title": placement.drive.job_title,
        "application_id": placement.application_id,
        "join_date": placement.join_date.isoformat() if placement.join_date else None,
        "package_lpa": placement.package_lpa,
        "offer_date": placement.offer_date.isoformat() if placement.offer_date else None,
        "placed_at": placement.placed_at.isoformat() if placement.placed_at else None,
        "resume_link": placement.application.resume_link if placement.application else None,
        "cover_letter": placement.application.cover_letter if placement.application else None,
    }


@common_bp.get("/public/avatar/company/<int:company_id>")
def company_avatar(company_id):
    company = Company.query.get_or_404(company_id)
    avatar_png = generate_avatar_png(company.email)
    return send_file(
        BytesIO(avatar_png),
        mimetype="image/png",
        as_attachment=False,
        download_name=f"company_{company_id}_avatar.png",
    )


@common_bp.get("/public/avatar/student/<int:student_id>")
def student_avatar(student_id):
    student = Student.query.get_or_404(student_id)
    avatar_png = generate_avatar_png(student.email)
    return send_file(
        BytesIO(avatar_png),
        mimetype="image/png",
        as_attachment=False,
        download_name=f"student_{student_id}_avatar.png",
    )


def _search_payload(role, query):
    cache_key = f"search:{role}:{query.lower()}"

    if role == Role.COMPANY.name:
        return _cached_payload(
            cache_key,
            lambda: {
                "role": "company",
                "query": query,
                "drives": [
                    _serialize_drive(drive)
                    for drive in PlacementDrive.query.filter(
                        or_(
                            PlacementDrive.job_title.ilike(f"%{query}%"),
                            PlacementDrive.job_description.ilike(f"%{query}%"),
                            PlacementDrive.eligibility_criteria.ilike(f"%{query}%"),
                            PlacementDrive.required_skills.ilike(f"%{query}%"),
                            PlacementDrive.experience_required.ilike(f"%{query}%"),
                            PlacementDrive.salary_range.ilike(f"%{query}%"),
                        )
                    ).all()
                ],
            },
            timeout=30,
        )

    if role == Role.ADMIN.name:
        return _cached_payload(
            cache_key,
            lambda: {
                "role": "admin",
                "query": query,
                "companies": [
                    _serialize_company(company)
                    for company in Company.query.filter(
                        or_(
                            Company.company_name.ilike(f"%{query}%"),
                            Company.email.ilike(f"%{query}%"),
                            Company.phone.ilike(f"%{query}%"),
                        )
                    ).all()
                ],
                "students": [
                    _serialize_student(student)
                    for student in Student.query.filter(
                        or_(
                            Student.name.ilike(f"%{query}%"),
                            Student.email.ilike(f"%{query}%"),
                            Student.phone.ilike(f"%{query}%"),
                        )
                    ).all()
                ],
                "drives": [
                    _serialize_drive(drive)
                    for drive in PlacementDrive.query.filter(
                        or_(
                            PlacementDrive.job_title.ilike(f"%{query}%"),
                            PlacementDrive.job_description.ilike(f"%{query}%"),
                            PlacementDrive.eligibility_criteria.ilike(f"%{query}%"),
                            PlacementDrive.required_skills.ilike(f"%{query}%"),
                            PlacementDrive.experience_required.ilike(f"%{query}%"),
                            PlacementDrive.salary_range.ilike(f"%{query}%"),
                        )
                    ).all()
                ],
            },
            timeout=30,
        )

    if role == Role.STUDENT.name:
        return _cached_payload(
            cache_key,
            lambda: {
                "role": "student",
                "query": query,
                "drives": [
                    _serialize_drive(drive)
                    for drive in PlacementDrive.query.filter(
                        (PlacementDrive.approval_status == ApprovalStatus.APPROVED)
                        & (PlacementDrive.company.has(Company.approval_status == ApprovalStatus.APPROVED))
                        & or_(
                            PlacementDrive.company.has(Company.company_name.ilike(f"%{query}%")),
                            PlacementDrive.job_title.ilike(f"%{query}%"),
                            PlacementDrive.job_description.ilike(f"%{query}%"),
                            PlacementDrive.eligibility_criteria.ilike(f"%{query}%"),
                            PlacementDrive.required_skills.ilike(f"%{query}%"),
                            PlacementDrive.experience_required.ilike(f"%{query}%"),
                            PlacementDrive.salary_range.ilike(f"%{query}%"),
                        )
                    ).all()
                ],
            },
            timeout=30,
        )

    return None


@common_bp.get("/public/search")
@jwt_required()
def search():
    identity = get_jwt_identity()
    claims = get_jwt()
    role = identity.get("role") if isinstance(identity, dict) else claims.get("role")
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify(message="Please enter a search query."), 400

    payload = _search_payload(role, query)
    if payload is None:
        return jsonify(message="Invalid user role for search."), 403

    return jsonify(payload)
