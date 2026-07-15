import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.factory import create_app
from backend.db import db
from backend.models.models import (
    Admin,
    ApprovalStatus,
    Application,
    ApplicationStatus,
    Company,
    DriveStatus,
    PlacementDrive,
    Student,
)


app = create_app()


def create_db(admin_email='admin@placementportal.com', admin_password='admin123'):
    db.create_all()
    if not Admin.query.filter_by(email=admin_email).first():
        admin = Admin(name='Admin', email=admin_email, phone='1236289108')
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin created with email: {admin_email} and password: {admin_password}")
    else:
        print("Admin already exists.")


def seed_data():
    if Student.query.first() or Company.query.first():
        print("Data already seeded, Skipping seeding.")
        return

    students = [
        Student(name="Alice Johnson", email="alice.johnson@example.com", phone="1234567890", bio="Passionate about software development and AI.", enrollment_number="ENR001", department="Computer Science", course="B.Tech", year_of_study=2),
        Student(name="Bob Smith", email="bob.smith@example.com", phone="0987654321", bio="Interested in embedded systems and IoT.", enrollment_number="ENR002", department="Electrical Engineering", course="B.Tech", year_of_study=3),
        Student(name="Charlie Brown", email="charlie.brown@example.com", phone="1122334455", bio="Enjoys working on mechanical design projects.", enrollment_number="ENR003", department="Mechanical Engineering", course="B.Tech", year_of_study=1),
        Student(name="Diana Prince", email="diana.prince@example.com", phone="5566778899", bio="Focused on sustainable engineering solutions.", enrollment_number="ENR004", department="Civil Engineering", course="B.Tech", year_of_study=4),
        Student(name="Ethan Hunt", email="ethan.hunt@example.com", phone="9988776655", bio="", enrollment_number="ENR005", department="Biotechnology", course="B.Tech", year_of_study=2),
        Student(name="Fiona Gallagher", email="fiona.gallagher@example.com", phone="1122334455", bio="", enrollment_number="ENR006", department="Chemical Engineering", course="B.Tech", year_of_study=3),
        Student(name="George Martin", email="george.martin@example.com", phone="1122334455", bio="", enrollment_number="ENR007", department="Aerospace Engineering", course="B.Tech", year_of_study=4),
        Student(name="Hannah Baker", email="hannah.baker@example.com", phone="1122334455", bio="", enrollment_number="ENR008", department="Biomedical Engineering", course="B.Tech", year_of_study=1),
        Student(name="Ian Fleming", email="ian.fleming@example.com", phone="1122334455", bio="", enrollment_number="ENR009", department="Materials Engineering", course="B.Tech", year_of_study=2),
        Student(name="Jane Doe", email="jane.doe@example.com", phone="1122334455", bio="", enrollment_number="ENR010", department="Industrial Engineering", course="B.Tech", year_of_study=3),
    ]
    for i, student in enumerate(students, start=1):
        student.set_password(f"password{i}")
    db.session.add_all(students)

    companies = [
        Company(name="Green Energy Solutions", email="green.energy@example.com", phone="0987654321", bio="Sustainable energy solutions provider", company_name="Green Energy Solutions Pvt Ltd", hr_contact="HR Manager", website="www.greenenergy.com", approval_status=ApprovalStatus.APPROVED),
        Company(name="HealthCare Plus", email="healthcare.plus@example.com", phone="1122334455", bio="Healthcare solutions provider", company_name="HealthCare Plus Pvt Ltd", hr_contact="HR Manager", website="www.healthcareplus.com", approval_status=ApprovalStatus.PENDING),
        Company(name="EduTech Global", email="edutech.global@example.com", phone="1122334455", bio="Educational technology solutions provider", company_name="EduTech Global Pvt Ltd", hr_contact="HR Manager", website="www.edutechglobal.com", approval_status=ApprovalStatus.APPROVED),
        Company(name="FinTech Solutions", email="fintech.solutions@example.com", phone="5544332211", bio="Financial technology solutions provider", company_name="FinTech Solutions Pvt Ltd", hr_contact="HR Manager", website="www.fintechsolutions.com", approval_status=ApprovalStatus.PENDING),
    ]
    for i, company in enumerate(companies, start=1):
        company.set_password(f"company{i}")
    db.session.add_all(companies)
    db.session.commit()

    # Add sample placement drives and applications so dashboard records are visible after seeding
    drives = [
        PlacementDrive(
            company_id=companies[0].id,
            job_title="Software Engineer Intern",
            job_description="Build features for student-facing placement applications.",
            eligibility_criteria="Computer Science students with strong coding skills.",
            drive_start_date=datetime.utcnow(),
            deadline=datetime.utcnow() + timedelta(days=30),
            salary_range="4-6 LPA",
            required_skills="Python, SQL, JavaScript",
            experience_required="Fresher",
            status=DriveStatus.ONGOING,
            approval_status=ApprovalStatus.APPROVED,
        ),
        PlacementDrive(
            company_id=companies[2].id,
            job_title="Data Analyst Trainee",
            job_description="Analyze placement data and support hiring decisions.",
            eligibility_criteria="Statistics, Mathematics, or Computer Science graduates.",
            drive_start_date=datetime.utcnow(),
            deadline=datetime.utcnow() + timedelta(days=20),
            salary_range="3-5 LPA",
            required_skills="Excel, Python, SQL",
            experience_required="Fresher",
            status=DriveStatus.ONGOING,
            approval_status=ApprovalStatus.APPROVED,
        ),
    ]
    db.session.add_all(drives)
    db.session.commit()

    applications = [
        Application(
            student_id=students[0].id,
            drive_id=drives[0].id,
            resume_link="https://example.com/resume/alice.pdf",
            cover_letter="I am excited to apply to this internship opportunity.",
            status=ApplicationStatus.APPLIED,
        ),
        Application(
            student_id=students[1].id,
            drive_id=drives[1].id,
            resume_link="https://example.com/resume/bob.pdf",
            cover_letter="I have strong analytical skills and would love to join.",
            status=ApplicationStatus.APPLIED,
        ),
    ]
    db.session.add_all(applications)
    db.session.commit()

    print("Sample data seeded successfully.")


if __name__ == '__main__':
    with app.app_context():
        create_db()
        seed_data()
    port = int(os.environ.get('PORT', os.environ.get('FLASK_RUN_PORT', '5001')))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

