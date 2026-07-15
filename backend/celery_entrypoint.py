#!/usr/bin/env python
"""Celery entrypoint for the backend package."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app import app  # noqa: E402
from backend.extensions import celery as celery_app  # noqa: E402

app = celery_app

if __name__ == "__main__":
    celery_app.start()
