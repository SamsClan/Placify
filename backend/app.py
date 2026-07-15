"""Backend Flask entrypoint."""

from backend.run import app


if __name__ == "__main__":
    app.run(debug=False)
