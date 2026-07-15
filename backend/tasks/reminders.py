from datetime import datetime, timedelta

from celery import shared_task
from flask import current_app, render_template
from flask_mail import Message

from backend.extensions import db, mail
from backend.models.models import Application, ApprovalStatus, Company, PlacementDrive, Student
from backend.utils.helpers import create_student_notification


@shared_task
def send_daily_deadline_reminders():
    try:
        reminder_window_days = current_app.config.get("REMINDER_DAYS_AHEAD", 30)
        try:
            reminder_window_days = int(reminder_window_days)
        except (TypeError, ValueError):
            reminder_window_days = 30

        if reminder_window_days < 1:
            reminder_window_days = 30

        now = datetime.utcnow()
        deadline_limit = now + timedelta(days=reminder_window_days)

        drives = (
            PlacementDrive.query.join(Company)
            .filter(
                PlacementDrive.approval_status == ApprovalStatus.APPROVED,
                Company.approval_status == ApprovalStatus.APPROVED,
                PlacementDrive.deadline >= now,
                PlacementDrive.deadline <= deadline_limit,
            )
            .all()
        )

        notified_count = 0
        failures = []

        for drive in drives:
            students = Student.query.filter_by(is_blacklisted=False).all()
            for student in students:
                existing_application = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
                if existing_application:
                    continue

                remaining_days = max((drive.deadline.date() - now.date()).days, 0)
                reminder_context = {
                    "student_name": student.name,
                    "company_name": drive.company.company_name if drive.company else "Unknown company",
                    "drive_title": drive.job_title,
                    "deadline": drive.deadline,
                    "remaining_days": remaining_days,
                }

                message_body = render_template("emails/deadline_reminder.txt", **reminder_context)
                html_body = render_template("emails/deadline_reminder.html", **reminder_context)

                try:
                    create_student_notification(
                        student.id,
                        (
                            f"Reminder: {drive.job_title} at {reminder_context['company_name']} "
                            f"expires in {remaining_days} day(s)."
                        ),
                        status="warning",
                    )
                    db.session.commit()

                    if student.email and current_app.config.get("MAIL_SERVER"):
                        subject = str(
                            current_app.config.get("REMINDER_EMAIL_SUBJECT", "Placement deadline reminder")
                            or "Placement deadline reminder"
                        )
                        sender = current_app.config.get("MAIL_DEFAULT_SENDER") or current_app.config.get("MAIL_USERNAME") or ""
                        msg = Message(
                            subject=subject,
                            sender=sender or None,
                            recipients=[student.email],
                        )
                        msg.body = message_body
                        msg.html = html_body
                        mail.send(msg)

                    notified_count += 1
                except Exception as exc:
                    db.session.rollback()
                    current_app.logger.exception("Failed to send reminder for %s (%s)", student.email, drive.job_title)
                    failures.append({"student": student.email, "drive": drive.job_title, "error": str(exc)})

        current_app.logger.info(
            "Daily reminder task completed: notified=%s, drives=%s, failures=%s",
            notified_count,
            len(drives),
            len(failures),
        )

        return {
            "status": "ok",
            "notified_count": notified_count,
            "drive_count": len(drives),
            "failures": failures,
        }
    except Exception as exc:
        current_app.logger.exception("Daily deadline reminder task failed")
        return {"status": "failed", "error": str(exc)}
