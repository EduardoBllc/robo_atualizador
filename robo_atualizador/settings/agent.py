from .base import *

import os
from django.core.exceptions import ImproperlyConfigured

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / '.env')

INSTALLED_APPS += [
    "agent",
    "runner",
    "scheduler",
]

def _get_bool(env_name: str, default: str = "0") -> bool:
    raw = os.getenv(env_name, default)
    val = str(raw).strip().lower()
    return val in {"1", "true", "yes", "on", "t", "y"}


CENTRAL_HOST = os.getenv("CENTRAL_HOST", "").strip()
CENTRAL_USES_TLS = _get_bool("CENTRAL_USES_TLS", "0")

_default_port = 443 if CENTRAL_USES_TLS else 80
_port_raw = os.getenv("CENTRAL_PORT", str(_default_port)).strip()

try:
    CENTRAL_PORT = int(_port_raw)
except ValueError as exc:
    raise ImproperlyConfigured(
        f"Variável de ambiente 'CENTRAL_PORT' inválida: '{_port_raw}'. Use um inteiro."
    ) from exc

if not CENTRAL_HOST:
    raise ImproperlyConfigured(
        "Variável de ambiente 'CENTRAL_HOST' é obrigatória para o papel 'agent'."
    )

CENTRAL_SCHEME = "https" if CENTRAL_USES_TLS else "http"
_needs_port = CENTRAL_PORT not in (80, 443)
CENTRAL_NETLOC = f"{CENTRAL_HOST}:{CENTRAL_PORT}" if _needs_port else CENTRAL_HOST
CENTRAL_BASE_URL = f"{CENTRAL_SCHEME}://{CENTRAL_NETLOC}"
