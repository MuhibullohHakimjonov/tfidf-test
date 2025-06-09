import os
from datetime import timedelta

import environ
from pathlib import Path
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
	DEBUG=(bool, False)
)

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
	env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=False)

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
    "http://localhost",
    "http://localhost:5173",
])

CORS_ALLOW_CREDENTIALS = True


ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'corsheaders',
	'rest_framework',
	'drf_spectacular',

	'tfidf',
	'user'
]

MIDDLEWARE = [
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',

	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / "templates"],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = "user.CustomUser"

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
	'DEFAULT_RENDERER_CLASSES': [
		'rest_framework.renderers.JSONRenderer',
	],
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	),
	'DEFAULT_THROTTLE_CLASSES': [
		'rest_framework.throttling.AnonRateThrottle',
		'rest_framework.throttling.UserRateThrottle',
	],
	'DEFAULT_THROTTLE_RATES': {
		'anon': '100/minute',
		'user': '100/minute',
	},
	'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': env('DATABASE_NAME'),
		'USER': env('POSTGRES_USER'),
		'PASSWORD': env('POSTGRES_PASSWORD'),
		'HOST': env('POSTGRES_HOST'),
		'PORT': env('POSTGRES_PORT')
	}
}

MONGO = {
	'USERNAME': env('MONGO_USERNAME'),
	'PASSWORD': env('MONGO_PASSWORD'),
	'HOST': env('MONGO_HOST'),
	'PORT': env.int('MONGO_PORT'),
	'DB_NAME': env('MONGO_DB_NAME'),
}

SIMPLE_JWT = {
	"ACCESS_TOKEN_LIFETIME": timedelta(days=1),
	"REFRESH_TOKEN_LIFETIME": timedelta(days=7)

}

REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env("REDIS_PORT", default="6379")

CACHES = {
	"default": {
		"BACKEND": "django_redis.cache.RedisCache",
		"LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
		"OPTIONS": {
			"CLIENT_CLASS": "django_redis.client.DefaultClient",
		}
	}
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# --- Email (Gmail SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
SERVER_EMAIL = env('EMAIL_HOST_USER')

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '{levelname} {asctime} {module} {message}',
			'style': '{',
		},
	},
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
			'formatter': 'verbose'
		},
	},
	'root': {
		'handlers': ['console'],
		'level': 'INFO',
	},
}

SPECTACULAR_SETTINGS = {
	'TITLE': 'My API',
	'DESCRIPTION': 'TF-IDF Document Analysis API',
	'VERSION': '1.0.0',
	'SERVE_INCLUDE_SCHEMA': False,
}
