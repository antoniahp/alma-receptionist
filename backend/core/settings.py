"""Configuración de Django. Todo lo que cambia entre entornos viene de variables de entorno (.env)."""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# override=True: si cambias el .env, al recargarse el servidor coge los valores nuevos
load_dotenv(BASE_DIR / ".env", override=True)


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "si", "sí"}


def env_list(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-cambia-esta-clave")
DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "domain.apps.DomainConfig",
    "infrastructure.apps.InfrastructureConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Mensajes de validación en el idioma del panel (cabecera Accept-Language: es o en)
    "django.middleware.locale.LocaleMiddleware",
    "infrastructure.language_middleware.ClientLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# SQLite en local; en Render/Docker se usa DATABASE_URL (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "es-es"
LANGUAGES = [("es", "Español"), ("en", "English")]
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Madrid")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["infrastructure.api.expiring_token_authentication.ExpiringTokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    # Límites por visitante: la web pública es barata; el chat gasta IA, así que tiene su propio límite
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("ANON_RATE_LIMIT", "2000/hour"),
        "chat": os.getenv("CHAT_RATE_LIMIT", "300/hour"),
        "chat_updates": "1200/hour",
    },
    "EXCEPTION_HANDLER": "infrastructure.api.exception_handler.custom_exception_handler",
}

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Correo (pedidos a proveedores). Por defecto se muestran en la consola.
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "hola@centro.example")

# Datos del negocio (white label: cambiando esto sirve para otro centro)
BUSINESS = {
    "name": os.getenv("BUSINESS_NAME", "Alma Estética"),
    "owner": os.getenv("BUSINESS_OWNER", "Cris"),
    "address": os.getenv("BUSINESS_ADDRESS", "Calle de la Luna 12, bajo"),
    "phone": os.getenv("BUSINESS_PHONE", "600 123 456"),
    "assistant_name": os.getenv("ASSISTANT_NAME", "Aura"),
    # Datos legales (aviso legal y privacidad). Hay que rellenarlos con los datos reales del centro.
    "legal_name": os.getenv("BUSINESS_LEGAL_NAME", ""),
    "nif": os.getenv("BUSINESS_NIF", ""),
    "email": os.getenv("BUSINESS_EMAIL", ""),
}
# Dirección pública de la web (para enlazar la política de privacidad desde Telegram)
PUBLIC_SITE_URL = os.getenv("PUBLIC_SITE_URL", "http://localhost:5173").rstrip("/")
# Enlace para dejar una reseña en Google. Vacío = no se piden reseñas.
GOOGLE_REVIEW_URL = os.getenv("GOOGLE_REVIEW_URL", "")

# Avisos emergentes en el navegador de la dueña (Web Push). Se generan con: python manage.py generate_vapid_keys
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:avisos@example.com")

# Modo demo (la web pública para el jurado del hackathon): no se envían correos de verdad,
# los datos de ejemplo se cargan de nuevo en cada arranque y la pantalla de entrada enseña el usuario de prueba.
DEMO_MODE = env_bool("DEMO_MODE", False)
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "demo")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo1234")
# Si es false, la demo funciona igual (datos de ejemplo, sin correos) pero la web no lo anuncia:
# ni aviso de "estás en la demo" ni usuario y contraseña en la pantalla de entrada (se dan aparte, p. ej. en el post).
DEMO_HINTS = env_bool("DEMO_HINTS", True)
# Horas que dura una sesión del panel antes de pedir de nuevo usuario y contraseña
PANEL_SESSION_HOURS = int(os.getenv("PANEL_SESSION_HOURS", "12"))
REVIEW_AFTER_VISITS = 3
SLOT_STEP_MINUTES = 30
BOOKING_DAYS_AHEAD = 21

# IA open-weight en local (Ollama + Gemma)
LLM_ENABLED = env_bool("LLM_ENABLED", True)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
# Solo para Ollama Cloud (OLLAMA_URL=https://ollama.com). En local se deja vacío.
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

# Comparador de precios de productos (SerpApi, búsqueda en Google Shopping). Sin clave, el comparador avisa.
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
SERPAPI_COUNTRY = os.getenv("SERPAPI_COUNTRY", "es")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")
TELEGRAM_OWNER_CHAT_ID = os.getenv("TELEGRAM_OWNER_CHAT_ID", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "application": {"handlers": ["console"], "level": "INFO"},
        "infrastructure": {"handlers": ["console"], "level": "INFO"},
    },
}
