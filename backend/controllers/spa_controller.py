"""
Serves the built Vue single-page app for every non-API route.

This replaces the old session-based Jinja controllers (auth_controller,
admin_controller, company_controller, student_controller, public_controller)
that rendered server-side templates. The frontend is now a Vue 3 SPA that
talks exclusively to the JSON API under /api/v1/*, so all UI routes
(/admin/dashboard, /student/jobs, deep links, browser refreshes, etc.) are
handled client-side by Vue Router once index.html loads.
"""

from pathlib import Path

from flask import current_app, jsonify, send_from_directory


def _dist_dir():
    """Locate the built frontend (frontend/dist) relative to the project root."""
    for base_dir in (Path(current_app.root_path), Path(current_app.root_path).parent):
        dist_dir = base_dir / "frontend" / "dist"
        if (dist_dir / "index.html").exists():
            return dist_dir
    return None


def register_routes(app):
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        dist_dir = _dist_dir()
        if dist_dir is None:
            return (
                jsonify(
                    message=(
                        "Frontend build not found. Run `npm install && npm run build` "
                        "inside the frontend/ directory, or use `npm run dev` for local development."
                    )
                ),
                404,
            )

        requested_file = dist_dir / path
        if path and requested_file.is_file():
            return send_from_directory(str(dist_dir), path)

        # Any other path (e.g. /admin/dashboard, /student/jobs/12) is a
        # client-side route — serve index.html and let Vue Router take over.
        return send_from_directory(str(dist_dir), "index.html")
