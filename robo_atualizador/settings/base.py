"""
Base Django settings shared by both Central and Cliente roles.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve base dir to the project root (repository root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env at the project root
load_dotenv(BASE_DIR / ".env")

ROLE = os.environ.get('ROLE', 'central').lower()
assert ROLE in ('central', 'agent'), "ROLE must be either 'central' or 'agent'"

IS_CENTRAL = ROLE == 'central'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-%k(bdf0j30o$w34x71g3%9m1i04%xd_j-gk7x$e+gs0z*3rgoz"

DEBUG = os.environ.get("DEBUG", "False") in ("1", "true", "True")

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
    "contracts",
    "authapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "robo_atualizador.urls"

WSGI_APPLICATION = "robo_atualizador.wsgi.application"

if DEBUG:
    # Database
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3" ,
            "NAME": BASE_DIR / f"db_{ROLE}.sqlite3",
        }
    }
else:
    # Build DB settings accepting POSTGRES_* first, then DATABASE_* as fallback
    DB_ENGINE = os.environ.get("DB_ENGINE", "django.db.backends.postgresql")
    DB_NAME = os.environ.get("DATABASE_NAME") or "robo_atualizador"
    DB_USER = os.environ.get("DATABASE_USER") or "postgres"
    DB_PASSWORD = os.environ.get("DATABASE_PASSWORD") or "p"
    DB_HOST = os.environ.get("DATABASE_HOST") or "localhost"
    DB_PORT = os.environ.get("DATABASE_PORT") or "5432"

    # Production database settings from environment variables
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en')
TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
