"""
ASGI config for robo_atualizador project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv
from django.core.asgi import get_asgi_application
from pathlib import Path

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    BASE_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(BASE_DIR / ".env")
    ROLE = os.environ.get('ROLE', 'central').lower()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"robo_atualizador.settings.{ROLE}")

application = get_asgi_application()
