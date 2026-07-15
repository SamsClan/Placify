from flask import Blueprint, jsonify

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@api_v1_bp.get("/health")
def health_check():
    return jsonify(
        status="ok",
        service="placement-portal-api",
        version="v1",
    )
