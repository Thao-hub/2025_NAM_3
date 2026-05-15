"""Django settings for webgis_store_locator."""

import hashlib
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file(BASE_DIR / '.env')

DEBUG = os.getenv('DJANGO_DEBUG', 'true').lower() in ('1', 'true', 'yes', 'on')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '').strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = hashlib.sha256(str(BASE_DIR.resolve()).encode('utf-8')).hexdigest()
    else:
        raise RuntimeError('Missing DJANGO_SECRET_KEY. Configure it in .env or the environment.')

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if h.strip()
]

INSTALLED_APPS = [
    'modules.store.apps.StoreConfig',
    'modules.spatial.apps.SpatialConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'modules.store.handlers.AdminErrorNotificationMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'modules.store.context_processors.store_shell',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'webgis_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', '123456'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'webgis-cache',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'vi'
LANGUAGES = [
    ('vi', 'Vietnamese'),
]
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_HOST = os.getenv('EMAIL_HOST', 'sandbox.smtp.mailtrap.io')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '2525'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'c2f709fb2a70b3').strip()
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '6e9af9edac71a0').strip()
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() in ('1', 'true', 'yes', 'on')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'false').lower() in ('1', 'true', 'yes', 'on')
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', '15'))
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Circle K & GS25 <no-reply@circlek-gs25.local>')
FEEDBACK_NOTIFICATION_EMAIL = os.getenv('FEEDBACK_NOTIFICATION_EMAIL', '').strip() or EMAIL_HOST_USER
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
    if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
    else 'django.core.mail.backends.console.EmailBackend',
)

# Optional: separate SMTP credentials for customer order emails.
ORDER_EMAIL_HOST = os.getenv('ORDER_EMAIL_HOST', EMAIL_HOST)
ORDER_EMAIL_PORT = int(os.getenv('ORDER_EMAIL_PORT', str(2525)))
ORDER_EMAIL_HOST_USER = os.getenv('ORDER_EMAIL_HOST_USER', 'ff1192c7434d62').strip() or EMAIL_HOST_USER
ORDER_EMAIL_HOST_PASSWORD = os.getenv('ORDER_EMAIL_HOST_PASSWORD', '5dfe2a4b6a990e').strip() or EMAIL_HOST_PASSWORD
ORDER_EMAIL_USE_TLS = os.getenv('ORDER_EMAIL_USE_TLS', str(EMAIL_USE_TLS)).lower() in ('1', 'true', 'yes', 'on')
ORDER_EMAIL_USE_SSL = os.getenv('ORDER_EMAIL_USE_SSL', str(EMAIL_USE_SSL)).lower() in ('1', 'true', 'yes', 'on')

TRASH_RETENTION_DAYS = int(os.getenv('TRASH_RETENTION_DAYS', '15'))
if TRASH_RETENTION_DAYS not in {7, 15}:
    TRASH_RETENTION_DAYS = 15

# Security defaults:
# - relaxed for local DEBUG
# - strict for production when DEBUG=False
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', str(not DEBUG)).lower() in ('1', 'true', 'yes', 'on')
SESSION_COOKIE_SECURE = os.getenv('DJANGO_SESSION_COOKIE_SECURE', str(not DEBUG)).lower() in ('1', 'true', 'yes', 'on')
CSRF_COOKIE_SECURE = os.getenv('DJANGO_CSRF_COOKIE_SECURE', str(not DEBUG)).lower() in ('1', 'true', 'yes', 'on')
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '0' if DEBUG else '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', str(not DEBUG)).lower() in ('1', 'true', 'yes', 'on')
SECURE_HSTS_PRELOAD = os.getenv('DJANGO_SECURE_HSTS_PRELOAD', str(not DEBUG)).lower() in ('1', 'true', 'yes', 'on')
SECURE_REFERRER_POLICY = os.getenv('DJANGO_SECURE_REFERRER_POLICY', 'strict-origin-when-cross-origin')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
