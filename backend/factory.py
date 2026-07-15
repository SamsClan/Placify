from datetime import datetime
from pathlib import Path
import os

from flask import Flask, jsonify, request

from backend.celery_app import init_celery
from backend.extensions import cache, cors, db, jwt, mail, migrate
from backend.config import Config

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = Path(__file__).resolve().parent
MIGRATIONS_DIR = BACKEND_ROOT / "migrations"
STORAGE_ROOT = BACKEND_ROOT / "storage"


def create_app(config_object=Config):
    app = Flask(
        __name__,
        template_folder=str(BACKEND_ROOT / "templates"),
        static_folder=str(STORAGE_ROOT / "uploads"),
    )
    app.config.from_object(config_object)
    app.config["UPLOAD_FOLDER"] = str(STORAGE_ROOT / "uploads" / "resumes")
    app.config["EXPORTS_DIR"] = str(STORAGE_ROOT / "exports")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["EXPORTS_DIR"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db, directory=str(MIGRATIONS_DIR))
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    init_celery(app)

    from backend.models.models import DriveStatus, PlacementDrive
    from backend.controllers.spa_controller import register_routes as register_spa
    from backend.api.v1 import register_routes as register_api_v1

    @app.before_request
    def auto_update_drive_statuses():
        now = datetime.utcnow()
        PlacementDrive.query.filter(
            PlacementDrive.status == DriveStatus.UPCOMING,
            PlacementDrive.drive_start_date <= now,
            PlacementDrive.deadline >= now,
        ).update({'status': DriveStatus.ONGOING}, synchronize_session=False)
        PlacementDrive.query.filter(
            PlacementDrive.status == DriveStatus.ONGOING,
            PlacementDrive.deadline < now,
        ).update({'status': DriveStatus.COMPLETED}, synchronize_session=False)
        PlacementDrive.query.filter(
            PlacementDrive.status == DriveStatus.UPCOMING,
            PlacementDrive.deadline < now,
        ).update({'status': DriveStatus.COMPLETED}, synchronize_session=False)
        db.session.commit()


    register_spa(app)

    @app.errorhandler(Exception)
    def handle_uncaught_exception(exc):
        if not request.path.startswith("/api/"):
            raise exc
        app.logger.exception("Unhandled error on %s", request.path)
        status = getattr(exc, "code", 500)
        if not isinstance(status, int) or status < 400:
            status = 500
        message = getattr(exc, "description", None) or str(exc) or "Internal server error."
        return jsonify(message=message, error="server_error"), status
    
    @app.after_request
    def prevent_api_caching(response):
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response

    return app


