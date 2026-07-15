from collections import Counter
from datetime import datetime, timedelta

from celery import shared_task
from flask import current_app, render_template
from flask_mail import Message

from backend.extensions import db, mail
from backend.models.models import (
    Admin,
    Application,
    ApplicationStatus,
    ApprovalStatus,
    Company,
    DriveStatus,
    PlacementDrive,
    Student,
)
from backend.utils import charts


@shared_task
def generate_monthly_activity_report():
    try:
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        drives = PlacementDrive.query.filter(
            PlacementDrive.drive_start_date >= month_start,
            PlacementDrive.drive_start_date <= month_end,
        ).all()

        total_drives = len(drives)
        total_companies = Company.query.count()
        total_applications = Application.query.count()
        selected_students = Application.query.filter_by(status=ApplicationStatus.SELECTED).count()
        selection_percentage = round((selected_students / total_applications * 100), 2) if total_applications else 0.0

        department_counter = Counter()
        status_counter = Counter()
        for application in Application.query.all():
            student = Student.query.get(application.student_id)
            if student and student.department:
                department_counter[student.department] += 1
            if application.status:
                status_counter[application.status.value] += 1

        drive_status_counter = {
            "Pending": PlacementDrive.query.filter_by(approval_status=ApprovalStatus.PENDING).count(),
            "Upcoming": PlacementDrive.query.filter_by(status=DriveStatus.UPCOMING).count(),
            "Ongoing": PlacementDrive.query.filter_by(status=DriveStatus.ONGOING).count(),
            "Completed": PlacementDrive.query.filter_by(status=DriveStatus.COMPLETED).count(),
        }

        drives_this_month = [
            {
                "title": drive.job_title,
                "company": drive.company.company_name if drive.company else "Unknown",
                "deadline": drive.deadline.strftime("%Y-%m-%d") if drive.deadline else "N/A",
            }
            for drive in drives
        ]

        top_companies = (
            db.session.query(Company.company_name, db.func.count(Application.id).label("application_count"))
            .join(PlacementDrive, PlacementDrive.company_id == Company.id)
            .join(Application, Application.drive_id == PlacementDrive.id)
            .group_by(Company.id)
            .order_by(db.desc("application_count"))
            .limit(5)
            .all()
        )

        # Applications & selections trend for the last 6 months (including current)
        trend_month_labels = []
        trend_application_counts = []
        trend_selected_counts = []
        for offset in range(5, -1, -1):
            month_index = today.month - offset
            year = today.year
            while month_index <= 0:
                month_index += 12
                year -= 1
            trend_month_start = today.replace(year=year, month=month_index, day=1)
            next_month = month_index + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1
            trend_month_end = today.replace(year=next_year, month=next_month, day=1)

            month_apps_query = Application.query.filter(
                Application.application_date >= trend_month_start,
                Application.application_date < trend_month_end,
            )
            trend_month_labels.append(trend_month_start.strftime("%b %Y"))
            trend_application_counts.append(month_apps_query.count())
            trend_selected_counts.append(
                month_apps_query.filter(Application.status == ApplicationStatus.SELECTED).count()
            )

        # Visual charts embedded directly in the email as base64 PNGs
        chart_applications_by_status = charts.applications_by_status_chart(
            {
                "Applied": status_counter.get("applied", 0),
                "Shortlisted": status_counter.get("shortlisted", 0),
                "Selected": status_counter.get("selected", 0),
                "Rejected": status_counter.get("rejected", 0),
            }
        )
        chart_drives_by_status = charts.drives_by_status_chart(drive_status_counter)
        chart_monthly_trend = charts.monthly_trend_chart(trend_month_labels, trend_application_counts, trend_selected_counts)
        chart_top_companies = charts.top_companies_chart(list(top_companies))
        chart_department_distribution = charts.department_distribution_chart(dict(department_counter))

        report_context = {
            "report_month": month_start.strftime("%B %Y"),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_drives": total_drives,
            "total_companies": total_companies,
            "total_applications": total_applications,
            "total_selected_students": selected_students,
            "selection_percentage": selection_percentage,
            "applications_by_department": sorted(department_counter.items(), key=lambda item: item[1], reverse=True),
            "drives_this_month": drives_this_month,
            "top_recruiting_companies": [
                {"name": company_name, "applications": count}
                for company_name, count in top_companies
            ],
            "chart_applications_by_status": chart_applications_by_status,
            "chart_drives_by_status": chart_drives_by_status,
            "chart_monthly_trend": chart_monthly_trend,
            "chart_top_companies": chart_top_companies,
            "chart_department_distribution": chart_department_distribution,
        }

        html_body = render_template("emails/monthly_activity_report.html", **report_context)
        subject = current_app.config.get("MONTHLY_REPORT_SUBJECT", "Monthly Activity Report")

        admin = Admin.query.first()
        if not admin:
            return {"status": "ok", "message": "No administrator found", "report": report_context}

        if admin.email and current_app.config.get("MAIL_SERVER"):
            subject = str(current_app.config.get("MONTHLY_REPORT_SUBJECT", "Monthly Activity Report") or "Monthly Activity Report")
            sender = current_app.config.get("MAIL_DEFAULT_SENDER") or current_app.config.get("MAIL_USERNAME") or ""
            message = Message(
                subject=subject,
                sender=sender or None,
                recipients=[admin.email],
            )
            message.html = html_body
            message.body = render_template("emails/monthly_activity_report.txt", **report_context)
            mail.send(message)

        current_app.logger.info("Monthly activity report generated for %s", admin.email)
        return {"status": "ok", "message": "Monthly activity report generated", "report": report_context}
    except Exception as exc:
        current_app.logger.exception("Monthly activity report generation failed")
        return {"status": "failed", "error": str(exc)}
