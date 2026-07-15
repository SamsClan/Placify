from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from backend.extensions import celery as celery_extension


def init_celery(app):
    celery_extension.conf.update(
        broker_url=app.config.get("CELERY_BROKER_URL") or app.config.get("REDIS_URL"),
        result_backend=app.config.get("CELERY_RESULT_BACKEND") or app.config.get("REDIS_URL"),
        task_serializer=app.config.get("CELERY_TASK_SERIALIZER", "json"),
        accept_content=app.config.get("CELERY_ACCEPT_CONTENT", ["json"]),
        result_serializer=app.config.get("CELERY_RESULT_SERIALIZER", "json"),
        timezone=app.config.get("CELERY_TIMEZONE", "UTC"),
        enable_utc=app.config.get("CELERY_ENABLE_UTC", True),
    )
    reminder_hour = int(app.config.get("REMINDER_SCHEDULE_HOUR", 9))
    reminder_minute = int(app.config.get("REMINDER_SCHEDULE_MINUTE", 0))

    celery_extension.conf.beat_schedule = {
        "daily-deadline-reminders": {
            "task": "backend.tasks.reminders.send_daily_deadline_reminders",
            "schedule": crontab(hour=reminder_hour, minute=reminder_minute),
        },
        "monthly-activity-report": {
            "task": "backend.tasks.reports.generate_monthly_activity_report",
            "schedule": crontab(day_of_month=1, hour=0, minute=0),
        },
    }

    class FlaskTask(celery_extension.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery_extension.Task = FlaskTask
    celery_extension.autodiscover_tasks(["backend.tasks"], force=True)
    app.extensions["celery"] = celery_extension
    app.celery = celery_extension
    return celery_extension
