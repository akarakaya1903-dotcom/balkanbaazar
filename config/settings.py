"""Balkanbaazar - Django ayarlari."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "market",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "market.middleware.VisitorCounterMiddleware",
    "market.middleware.ThrottleMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "market.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# Sunucuda (Render vb.) DATABASE_URL tanimliysa PostgreSQL kullanilir.
if os.environ.get("DATABASE_URL"):
    import dj_database_url
    DATABASES["default"] = dj_database_url.config(conn_max_age=600)
# Production icin PostgreSQL ornegi:
# DATABASES["default"] = {
#     "ENGINE": "django.db.backends.postgresql",
#     "NAME": os.environ["DB_NAME"], "USER": os.environ["DB_USER"],
#     "PASSWORD": os.environ["DB_PASSWORD"], "HOST": os.environ.get("DB_HOST", "localhost"),
#     "PORT": os.environ.get("DB_PORT", "5432"),
# }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Skopje"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
# Kalici disk baglarsan MEDIA_ROOT ortam degiskeniyle o klasore isaret ettir (orn. /var/data/media).
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# --- Sunucu (HTTPS arkasinda) ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
_render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
if _render_url:
    CSRF_TRUSTED_ORIGINS.append(_render_url)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "market:login"
LOGIN_REDIRECT_URL = "market:panel"
LOGOUT_REDIRECT_URL = "market:home"

# --- Balkanbaazar ---
SITE_NAME = "Balkan Baazar"
SITE_HQ = "Makedonska 1, 1000 Skopje / Uskup, Kuzey Makedonya"
DEFAULT_COUNTRY = "MK"
DEFAULT_LANG = "tr"
SHOP_PLAN_FREE_MONTHS = 3
SHOP_PLAN_MID_PRICE_EUR = 9
SHOP_PLAN_MID_UNTIL_MONTH = 9
SHOP_PLAN_FULL_PRICE_EUR = 29

# --- Odeme (Stripe) ---
# Test anahtarlarini https://dashboard.stripe.com/test/apikeys adresinden al.
# Bos birakilirsa site otomatik olarak demo odeme akisina duser (gercek tahsilat yapilmaz).
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
SITE_URL = os.environ.get("SITE_URL", os.environ.get("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000"))

# --- E-posta bildirimleri ---
# Varsayilan: konsol backend (e-postalar terminale yazilir, SMTP kurmaya gerek yok).
# Gercek gonderim icin EMAIL_BACKEND'i smtp backend'e cevirip host/kullanici/sifre tanimla.
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "Balkan Baazar <no-reply@balkanbaazar.com>"
)
# Yeni magaza basvurusu geldiginde haber verilecek yonetici adresleri (virgulle ayir).
STAFF_NOTIFY_EMAILS = [e.strip() for e in os.environ.get("STAFF_NOTIFY_EMAILS", "").split(",") if e.strip()]

# --- Ilan one cikarma (ucretli vitrin) paketleri ---
BOOST_PACKAGES = [
    {"days": 3, "price_eur": 2},
    {"days": 7, "price_eur": 5},
    {"days": 30, "price_eur": 15},
]

# Ilan basina fotograf siniri (kapak dahil toplam)
MIN_LISTING_IMAGES = int(os.environ.get("MIN_LISTING_IMAGES", "20"))
MAX_LISTING_IMAGES = int(os.environ.get("MAX_LISTING_IMAGES", "50"))

# Cok fotografli / videolu yuklemeler
DATA_UPLOAD_MAX_NUMBER_FILES = 300
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000
MAX_VIDEO_MB = int(os.environ.get("MAX_VIDEO_MB", "300"))
MAX_VIDEO_SECONDS = int(os.environ.get("MAX_VIDEO_SECONDS", "240"))

# Google ile giris (Google Cloud Console > OAuth istemcisi)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
LISTING_DAYS = int(os.environ.get("LISTING_DAYS", "60"))

# Sunucu hatalari (500) yoneticilere e-posta ile bildirilir (DEBUG kapaliyken)
ADMINS = [("Yonetici", e) for e in STAFF_NOTIFY_EMAILS]
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
