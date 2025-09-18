"""
Development settings for testing without SQL Server
"""

from .settings import *
from pathlib import Path

# Define BASE_DIR for this settings file
BASE_DIR = Path(__file__).resolve().parent.parent

# Override database with SQLite for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_dev.sqlite3",
    }
}

# Disable debug toolbar for testing
# MIDDLEWARE = [
#     m for m in MIDDLEWARE if m != "debug_toolbar.middleware.DebugToolbarMiddleware"
# ]

# Simple logging for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
    },
    "loggers": {
        "entities.generator": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
