from .routes import api_v1_bp
from .auth_routes import auth_bp
from .common import common_bp
from .admin_routes import admin_bp
from .company_routes import company_bp
from .student_routes import student_bp


def register_routes(app):
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
