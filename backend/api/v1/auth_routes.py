from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from backend.db import db
from backend.models.models import Admin, ApprovalStatus, Company, Role, Student
from backend.utils.helpers import is_valid_website, save_resume_file


auth_bp = Blueprint("api_v1_auth", __name__, url_prefix="/api/v1/auth")


def _serialize_user(user):
    payload = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role.name,
    }

    if isinstance(user, Student):
        payload.update(
            {
                "department": user.department,
                "course": user.course,
                "year_of_study": user.year_of_study,
                "skills": user.skills,
                "resume_link": (request.url_root.rstrip('/') + user.resume_link) if user.resume_link and not user.resume_link.startswith(('http://','https://')) else user.resume_link,
                "is_blacklisted": user.is_blacklisted,
            }
        )
    elif isinstance(user, Company):
        payload.update(
            {
                "company_name": user.company_name,
                "hr_contact": user.hr_contact,
                "website": user.website,
                "approval_status": user.approval_status.value,
            }
        )
    elif isinstance(user, Admin):
        payload.update({"is_active": user.is_active})

    return payload


def _find_user_by_email(email):
    return (
        Admin.query.filter_by(email=email).first()
        or Company.query.filter_by(email=email).first()
        or Student.query.filter_by(email=email).first()
    )


def _get_identity_payload():
    identity = get_jwt_identity()
    claims = get_jwt()

    if isinstance(identity, dict):
        user_id = identity.get("user_id")
        role = identity.get("role")
        email = identity.get("email")
    else:
        user_id = identity
        role = claims.get("role")
        email = claims.get("email")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        pass

    return {"user_id": user_id, "role": role, "email": email}


def _load_user_from_payload(payload):
    user_id = payload.get("user_id")
    role = payload.get("role")

    if role == Role.ADMIN.name:
        return Admin.query.get(user_id)
    if role == Role.COMPANY.name:
        return Company.query.get(user_id)
    if role == Role.STUDENT.name:
        return Student.query.get(user_id)
    return None


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify(message="Email and password are required."), 400

    user = _find_user_by_email(email)
    if not user or not user.check_password(password):
        return jsonify(message="Invalid email or password."), 401

    if isinstance(user, Student) and user.is_blacklisted:
        return jsonify(message="Your account has been blacklisted."), 403

    if isinstance(user, Company) and user.approval_status != ApprovalStatus.APPROVED:
        return jsonify(message="Your company registration is pending approval."), 403

    identity = str(user.id)
    claims = {"role": user.role.name, "email": user.email}

    return jsonify(
        message="Login successful.",
        user=_serialize_user(user),
        access_token=create_access_token(identity=identity, additional_claims=claims),
        refresh_token=create_refresh_token(identity=identity, additional_claims=claims),
    )


@auth_bp.post("/register/student")
def register_student():
    is_multipart = request.content_type and "multipart/form-data" in request.content_type
    data = request.form if is_multipart else (request.get_json(silent=True) or {})

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()
    enrollment_number = (data.get("enrollment_number") or "").strip()
    department = (data.get("department") or "").strip()
    course = (data.get("course") or "").strip()
    year_of_study = data.get("year_of_study")
    bio = (data.get("bio") or "").strip()
    skills = (data.get("skills") or "").strip()
    resume_link = (data.get("resume_link") or "").strip()
    terms_accepted = data.get("terms_accepted")
    if is_multipart:
        terms_accepted = str(terms_accepted).lower() in ("true", "1", "on", "yes")

    errors = []

    resume_file_url = None
    if is_multipart and request.files.get("resume"):
        try:
            resume_file_url = save_resume_file(request.files.get("resume"))
        except ValueError as exc:
            errors.append(str(exc))
    if resume_file_url:
        resume_link = resume_file_url

    if not name or len(name) < 2:
        errors.append("Full name must be at least 2 characters long.")
    if len(name) > 100:
        errors.append("Full name cannot exceed 100 characters.")

    if not email:
        errors.append("Email is required.")
    elif "@" not in email or "." not in email:
        errors.append("Please enter a valid email address.")
    elif _find_user_by_email(email):
        errors.append("This email is already registered.")

    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    elif not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        errors.append("Password must contain uppercase, lowercase, and numeric characters.")

    if not phone or len(phone) < 10:
        errors.append("Please enter a valid phone number.")

    if not enrollment_number or len(enrollment_number) < 2:
        errors.append("Enrollment number must be at least 2 characters long.")
    elif Student.query.filter_by(enrollment_number=enrollment_number).first():
        errors.append("This enrollment number is already registered.")

    if not department or len(department) < 2:
        errors.append("Please enter a valid department.")
    if not course or len(course) < 2:
        errors.append("Course name must be at least 2 characters long.")
    try:
        year_of_study = int(year_of_study)
        if year_of_study < 1 or year_of_study > 4:
            errors.append("Year of study must be between 1 and 4.")
    except (TypeError, ValueError):
        errors.append("Year of study must be a valid number.")

    if bio and len(bio) > 500:
        errors.append("Bio cannot exceed 500 characters.")
    if skills and len(skills) > 200:
        errors.append("Skills cannot exceed 200 characters.")
    if resume_link and len(resume_link) > 200:
        errors.append("Resume URL cannot exceed 200 characters.")
    if resume_link and not resume_file_url and not (resume_link.startswith("http://") or resume_link.startswith("https://")):
        errors.append("Resume URL must start with http:// or https://")

    if not terms_accepted:
        errors.append("You must accept the Terms and Conditions to register.")

    if errors:
        return jsonify(message="Validation failed.", errors=errors), 400

    student = Student(
        name=name,
        email=email,
        phone=phone,
        enrollment_number=enrollment_number,
        department=department,
        course=course,
        year_of_study=year_of_study,
        bio=bio or None,
        skills=skills or None,
        resume_link=resume_link or None,
    )
    student.set_password(password)
    db.session.add(student)
    db.session.commit()

    return jsonify(message="Student registered successfully.", user=_serialize_user(student)), 201


@auth_bp.post("/register/company")
def register_company():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()
    company_name = (data.get("company_name") or "").strip()
    bio = (data.get("bio") or "").strip()
    hr_contact = (data.get("hr_contact") or "").strip()
    website = (data.get("website") or "").strip()
    terms_accepted = data.get("terms_accepted")

    errors = []
    if not name or len(name) < 2:
        errors.append("Full name must be at least 2 characters long.")
    if len(name) > 100:
        errors.append("Full name cannot exceed 100 characters.")

    if not email:
        errors.append("Email is required.")
    elif "@" not in email or "." not in email:
        errors.append("Please enter a valid email address.")
    elif _find_user_by_email(email):
        errors.append("This email is already registered.")

    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    elif not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        errors.append("Password must contain uppercase, lowercase, and numeric characters.")

    if not phone or len(phone) < 10:
        errors.append("Please enter a valid phone number.")

    if not company_name or len(company_name) < 2:
        errors.append("Company name must be at least 2 characters long.")
    elif Company.query.filter_by(company_name=company_name).first():
        errors.append("This company name is already registered.")

    if website and not is_valid_website(website):
        errors.append("Website URL must be a valid domain or full URL (for example, www.example.com or https://example.com)")
    if website and len(website) > 200:
        errors.append("Website URL cannot exceed 200 characters.")

    if bio and len(bio) > 500:
        errors.append("Company bio cannot exceed 500 characters.")
    if hr_contact and len(hr_contact) > 100:
        errors.append("HR contact name cannot exceed 100 characters.")

    if not terms_accepted:
        errors.append("You must accept the Terms and Conditions to register your company.")

    if errors:
        return jsonify(message="Validation failed.", errors=errors), 400

    company = Company(
        name=name,
        email=email,
        phone=phone,
        company_name=company_name,
        hr_contact=hr_contact or None,
        website=website or None,
        bio=bio or None,
        approval_status=ApprovalStatus.PENDING,
    )
    company.set_password(password)
    db.session.add(company)
    db.session.commit()

    return jsonify(message="Company registered successfully.", user=_serialize_user(company)), 201


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = _load_user_from_payload(_get_identity_payload())
    if not user:
        return jsonify(message="User not found."), 404

    return jsonify(
        access_token=create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role.name, "email": user.email},
        ),
        user=_serialize_user(user),
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    user = _load_user_from_payload(_get_identity_payload())
    if not user:
        return jsonify(message="User not found."), 404

    return jsonify(user=_serialize_user(user))