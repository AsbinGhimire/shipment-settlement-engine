"""
Django settings for AccountEase project.

This module contains the configuration for the Django project, including:
- Database configuration (MySQL)
- Security settings (SSL, HSTS, etc.)
- Application definition (Installed apps, Middleware)
- Authentication and Password validation
- Static and Media files configuration
- Third-party integrations (REST Framework, CORS)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------
# Base Directory & .env Loading
# --------------------------------------------------
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a .env file located at the BASE_DIR
load_dotenv(BASE_DIR / ".env")

# --------------------------------------------------
# Security
# --------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

# [NEW] Production Security Settings
if not DEBUG:
    # Consistency & HTTPS Enforcement
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE & CSRF_COOKIE_SECURE are handled in the Sessions section
    
    # HSTS (Strict-Transport-Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Content Security Policy (Optional but recommended - minimal setup)
    # SECURE_CONTENT_TYPE_NOSNIFF = True


ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,*"
).split(",")

# --------------------------------------------------
# Application Definition
# --------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Local apps
    'shipments',
    'forgotapp',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # [NEW] Production static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------------------------------
# CORS / CSRF
# --------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = DEBUG  # allow all only in dev

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# --------------------------------------------------
# URLs
# --------------------------------------------------
ROOT_URLCONF = 'accountease.urls'
WSGI_APPLICATION = 'accountease.wsgi.application'

# --------------------------------------------------
# Templates
# --------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'shipments.context_processors.rbac_flags'

            ],
        },
    },
]

# --------------------------------------------------
# Database (MySQL)
# --------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# --------------------------------------------------
# Email
# --------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --------------------------------------------------
# Authentication
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# Sessions & Cookies
# --------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Secure and persistent
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Security best practice for sensitive apps
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access to session cookie
CSRF_COOKIE_HTTPONLY = False  # False is default (needed for AJAX), set True if no JS CSRF needed

# Secure flags (Enabled in Production only)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'shipments:shipment_list'
LOGOUT_REDIRECT_URL = '/'

# --------------------------------------------------
# Internationalization & Date Format
# --------------------------------------------------
LANGUAGE_CODE = 'en-gb'  # dd/mm/yyyy
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

DATE_INPUT_FORMATS = [
    '%d/%m/%Y',
    '%Y-%m-%d',
]

# --------------------------------------------------
# Static & Media
# --------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# [NEW] Whitenoise Configuration
# Enable compression and caching for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


if os.getenv("USE_MEDIA", "False") == "True":
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------
# Django REST Framework
# --------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# [NEW] Production Logging
# Ensure errors are logged to console (useful for containerized envs like Docker/Heroku)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

