from backend.db import db
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash

#Enum

class Role(Enum):
    STUDENT = 'student'
    COMPANY = 'company'
    ADMIN = 'admin'

class ApprovalStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    BLACKLISTED = 'blacklisted'

class DriveStatus(Enum):
    UPCOMING = 'upcoming'
    ONGOING = 'ongoing'
    COMPLETED = 'completed' 

class ApplicationStatus(Enum):
    APPLIED = 'applied'
    SHORTLISTED = 'shortlisted'
    REJECTED = 'rejected'
    SELECTED = 'selected'

class UserMixin(db.Model):
    __abstract__ = True #Used because we don't want to create a separate table for UserMixin
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column("password",db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):     
        self._password_hash = generate_password_hash(password)  
    
    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

class Admin(UserMixin):
    __tablename__ = 'admins'
    role = db.Column(db.Enum(Role), default=Role.ADMIN, nullable=False)

    def __repr__(self):
        return f"<Admin {self.name} ({self.email})>"

class Company(UserMixin):
    __tablename__ = 'companies'
    role = db.Column(db.Enum(Role), default=Role.COMPANY, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    company_name = db.Column(db.String(150), unique=True, nullable=False)
    hr_contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True) 
    approval_status = db.Column(db.Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade="all, delete-orphan")

    def is_approved(self):
        return self.approval_status == ApprovalStatus.APPROVED
    
    def __repr__(self):
        return f"<Company {self.name} ({self.email}) - {self.approval_status.value}>" 

class Student(UserMixin):
    __tablename__ = 'students'
    role = db.Column(db.Enum(Role), default=Role.STUDENT, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    enrollment_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    skills = db.Column(db.String(200), nullable=True)
    resume_link = db.Column(db.String(200), nullable=True)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)
    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship('StudentNotification', backref='student', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.name} ({self.email}) - Roll: {self.roll_number}>"

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    drive_start_date = db.Column(db.DateTime, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    salary_range = db.Column(db.String(50), nullable=True)
    required_skills = db.Column(db.String(200), nullable=True)
    experience_required = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Enum(DriveStatus), default=DriveStatus.UPCOMING, nullable=False)
    approval_status = db.Column(db.Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    applications = db.relationship('Application', backref='drive', lazy=True, cascade="all, delete-orphan")

    @property
    def computed_status(self):
        """Derive drive status from dates, ignoring the stored DB value."""
        now = datetime.utcnow()
        if now < self.drive_start_date:
            return DriveStatus.UPCOMING
        elif now <= self.deadline:
            return DriveStatus.ONGOING
        else:
            return DriveStatus.COMPLETED


    def __repr__(self):
        return f"<PlacementDrive {self.job_title} at {self.company.company_name} on {self.drive_date}>"

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id', ondelete='CASCADE'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    resume_link = db.Column(db.String(200), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Application {self.student.name} for {self.drive.job_title} at {self.drive.company.company_name}>"

class StudentNotification(db.Model):
    __tablename__ = 'student_notifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='info', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    application = db.relationship('Application', backref=db.backref('notifications', lazy=True, cascade="all, delete-orphan"), lazy=True)

    def __repr__(self):
        return f"<StudentNotification {self.student_id} {self.status}>"

class Placemment(db.Model):
    __tablename__ = 'placements'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id', ondelete='CASCADE'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    offer_date = db.Column(db.DateTime, default=datetime.utcnow)
    join_date = db.Column(db.DateTime, nullable=True)
    package_lpa = db.Column(db.String(50), nullable=True)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # relationships for convenient access in serializers and templates
    student = db.relationship('Student', backref=db.backref('placements', lazy=True), lazy=True)
    company = db.relationship('Company', lazy=True)
    drive = db.relationship('PlacementDrive', lazy=True)
    application = db.relationship('Application', backref=db.backref('placement', uselist=False), lazy=True)

    def __repr__(self):
        student_name = getattr(self, 'student', None) and getattr(self.student, 'name', 'unknown')
        company_name = getattr(self, 'company', None) and getattr(self.company, 'company_name', 'unknown')
        drive_title = getattr(self, 'drive', None) and getattr(self.drive, 'job_title', 'unknown')
        return f"<Placement {student_name} at {company_name} for {drive_title}>"
    
