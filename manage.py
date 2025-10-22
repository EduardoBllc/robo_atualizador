#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv

from robo_atualizador.settings.base import BASE_DIR


def main():
    """Run administrative tasks."""
    load_dotenv(BASE_DIR / '.env')
    role = os.environ.get('ROLE', 'central').lower()

    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"robo_atualizador.settings.{role}")

    if os.environ.get('RUN_MAIN', 'false').lower() == 'false':
        print("")
        print(f"Running as {role.upper()}")
        print("")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
