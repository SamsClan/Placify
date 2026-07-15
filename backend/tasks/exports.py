import csv
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from celery import shared_task
from flask import current_app

from backend.extensions import db
from backend.models.models import Application, ApplicationStatus, PlacementDrive, Student
from backend.utils.helpers import create_student_notification


def _export_dir():
    configured_dir = current_app.config.get("EXPORTS_DIR") or "storage/exports"
    export_path = Path(configured_dir)
    if not export_path.is_absolute():
        export_path = Path(current_app.root_path) / export_path
    export_path.mkdir(parents=True, exist_ok=True)
    return export_path


def cleanup_expired_exports(expire_hours=None):
    export_dir = _export_dir()
    expire_hours = expire_hours if expire_hours is not None else current_app.config.get("EXPORT_RETENTION_HOURS", 24)
    cutoff_time = datetime.utcnow() - timedelta(hours=expire_hours)
    deleted_files = []

    for export_file in export_dir.glob("*.csv"):
        try:
            if datetime.fromtimestamp(export_file.stat().st_mtime) < cutoff_time:
                export_file.unlink(missing_ok=True)
                deleted_files.append(export_file.name)
        except FileNotFoundError:
            continue

    return deleted_files


@shared_task
def export_student_applications(student_id, student_name=None, student_email=None):
    try:
        cleanup_expired_exports()
        export_dir = _export_dir()
        filename = f"student_{student_id}_{uuid.uuid4().hex}.csv"
        export_path = export_dir / filename

        applications = (
            Application.query.filter_by(student_id=student_id)
            .join(PlacementDrive)
            .order_by(Application.application_date.desc())
            .all()
        )

        with export_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                "Student ID",
                "Student Name",
                "Company Name",
                "Drive Title",
                "Application Status",
                "Applied Date",
                "Updated Date",
            ])
            for application in applications:
                writer.writerow([
                    application.student_id,
                    student_name or (application.student.name if application.student else ""),
                    application.drive.company.company_name if application.drive and application.drive.company else "",
                    application.drive.job_title if application.drive else "",
                    application.status.value if application.status else ApplicationStatus.APPLIED.value,
                    application.application_date.isoformat() if application.application_date else "",
                    application.application_date.isoformat() if application.application_date else "",
                ])

        if student_id:
            create_student_notification(
                student_id,
                "Your application export is ready. Download it from the notification area.",
                status="success",
            )
            db.session.commit()

        current_app.logger.info("Export completed for student %s: %s", student_id, filename)
        return {
            "status": "ok",
            "filename": filename,
            "student_id": student_id,
            "row_count": len(applications),
        }
    except Exception as exc:
        current_app.logger.exception("Student export failed for student %s", student_id)
        if student_id:
            create_student_notification(
                student_id,
                "Your application export failed. Please try again later.",
                status="danger",
            )
            db.session.commit()
        return {"status": "failed", "error": str(exc), "student_id": student_id}
