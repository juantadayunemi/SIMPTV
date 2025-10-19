#!/usr/bin/env python
import os
import sys


def load_dotenv(path: str = ".env"):
    """Minimal .env loader: parse KEY=VALUE lines and set os.environ if not already set.

    This avoids adding external dependencies while allowing centralization of PORT.
    """
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        # Don't fail startup just because .env couldn't be read
        pass


if __name__ == "__main__":
    # Load .env early so subsequent logic (default port) can read it.
    load_dotenv()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gov_vehicle_report.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH?"
        ) from exc

    # If user runs `python manage.py runserver` without port, append PORT from env or fallback to 7000
    if len(sys.argv) >= 2 and sys.argv[1] == "runserver" and len(sys.argv) == 2:
        port = os.environ.get("PORT", "7000")
        sys.argv.append(port)

    execute_from_command_line(sys.argv)
