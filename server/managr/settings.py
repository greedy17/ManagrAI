import os
import dj_database_url


def _env_get_required(setting_name):
    """Get the value of an environment variable and assert that it is set."""
    setting = os.environ.get(setting_name)
    assert setting not in {
        None,
        "",
    }, "{0} must be defined as an environment variable.".format(setting_name)
    return setting


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
IN_DEV = ENVIRONMENT == "development"
IN_STAGING = ENVIRONMENT == "staging"
IN_PROD = ENVIRONMENT == "production"
IN_CI = os.environ.get("IN_CI") == "True"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = _env_get_required("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _env_get_required("DEBUG") == "True"

if IN_DEV:
    SERVER_EMAIL = "Managr Development <noreply-dev@managr.com>"
elif IN_STAGING:
    SERVER_EMAIL = "Managr Staging <noreply-staging@managr.com>"
else:
    SERVER_EMAIL = "Managr <noreply@managr.com>"

DEFAULT_FROM_EMAIL = SERVER_EMAIL

# Email address of the staff who should receive certain emails
STAFF_EMAIL = _env_get_required("STAFF_EMAIL")

#
# Domain Configuration
#
CURRENT_DOMAIN = _env_get_required("CURRENT_DOMAIN")
CURRENT_PORT = os.environ.get("CURRENT_PORT")
ALLOWED_HOSTS = []
ALLOWED_HOSTS += _env_get_required("ALLOWED_HOSTS").split(",")
if CURRENT_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(CURRENT_DOMAIN)


# Application definition

INSTALLED_APPS = [
    # Local
    "managr.core",
    "managr.api",
    "managr.lead",
    "managr.organization",
    "managr.polling",
    "managr.report",
    "managr.slack",
    "managr.zoom",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third Party
    "django_nose",
    "storages",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "django_extensions",
    "background_task",
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
]

ROOT_URLCONF = "managr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "../client/dist/"),],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "managr.wsgi.application"


# Database
"""There are two ways to specifiy the database connection

1. Heroku - we use dj_database_url to interpret Heroku's DATABASE_URL env variable.
2. Specify DB_NAME, DB_USER, DB_PASS, and DB_HOST Directly in the env file.
"""
# Update database configuration with dj_database_url
heroku_db_from_env = dj_database_url.config()
if bool(heroku_db_from_env):
    DATABASES = {"default": heroku_db_from_env}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": _env_get_required("DB_NAME"),
            "USER": _env_get_required("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASS", ""),
            "HOST": _env_get_required("DB_HOST"),
            "CONN_MAX_AGE": 600,
        }
    }

#
# User Configuration and Password Validation
#
AUTH_USER_MODEL = "core.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10,},
    },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

#
# Internationalization & Localization Settings
#
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

#
# Django Rest Framework Configuration
#
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": ("managr.core.pagination.PageNumberPagination"),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

#
# Static files (CSS, JavaScript, Images)
#
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media-files")

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "../client/dist/static")]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# fixtures
FIXTURE_DIRS = ["organization/fixtures/"]


# Django Storages configuration
USE_AWS_STORAGE = os.environ.get("USE_AWS_STORAGE") == "True" or False
if USE_AWS_STORAGE:
    AWS_ACCESS_KEY_ID = _env_get_required("AWS_ACCESS_KEY_ID")
    AWS_STORAGE_BUCKET_NAME = _env_get_required("AWS_STORAGE_BUCKET_NAME")
    AWS_SECRET_ACCESS_KEY = _env_get_required("AWS_SECRET_ACCESS_KEY")
    AWS_S3_CUSTOM_DOMAIN = AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com"
    # change this to check for env
    AWS_LOCATION = os.environ.get("AWS_LOCATION", "")

    MEDIAFILES_LOCATION = AWS_LOCATION + "/media"
    DEFAULT_FILE_STORAGE = "managr.core.handlers.PrivateMediaStorage"

# Maximum size, in bytes, of a request before it will be streamed to the
# file system instead of into memory.
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB

# Maximum size in bytes of request data (excluding file uploads) that will be
# read before a SuspiciousOperation (RequestDataTooBig) is raised.
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # i.e. 100 MB


#
# Email settings
#
USE_CUSTOM_SMTP = os.environ.get("USE_CUSTOM_SMTP")
if USE_CUSTOM_SMTP == "True":
    EMAIL_HOST = _env_get_required("SMTP_HOST")
    EMAIL_PORT = os.environ.get("SMTP_PORT", 587)
    EMAIL_HOST_USER = _env_get_required("SMTP_USER")
    EMAIL_HOST_PASSWORD = _env_get_required("SMTP_PASSWORD")
    EMAIL_ALLOWED_DOMAINS = _env_get_required("SMTP_VALID_TESTING_DOMAINS")
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

#
# HTTPS Everywhere outside the dev environment
#
if not IN_DEV:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    MIDDLEWARE += [
        "django.middleware.security.SecurityMiddleware",
    ]


#
# Custom logging configuration
#
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue",},
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {
            "format": "[%(asctime)s] %(levelname)s %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "mail_admins": {
            "level": "WARNING",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "mail_admins"], "level": "INFO",},
        # The logger name matters -- it MUST match the name of the app
        "managr": {
            "handlers": ["console", "mail_admins",],
            "level": "DEBUG",
            "propagate": True,
        },
        "managr.request": {"handlers": [], "level": "INFO", "propagate": True},
        "managr.tasks": {"handlers": [], "level": "INFO", "propagate": True},
    },
}

# Popular testing framework that allows logging to stdout while running unit tests
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

# Rollbar error logging
if _env_get_required("USE_ROLLBAR") == "True":
    MIDDLEWARE += [
        "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
    ]
    ROLLBAR = {
        "access_token": _env_get_required("ROLLBAR_ACCESS_TOKEN"),
        "environment": ENVIRONMENT,
        "branch": "master",
        "root": BASE_DIR,
    }
    LOGGING["handlers"].update(
        {
            # Rollbar exception logging handler
            "rollbar": {
                "level": "WARNING",
                "filters": ["require_debug_false"],
                "access_token": _env_get_required("ROLLBAR_ACCESS_TOKEN"),
                "environment": ENVIRONMENT,
                "class": "rollbar.logger.RollbarHandler",
            },
        }
    )
    LOGGING["loggers"]["django"]["handlers"].remove("mail_admins")
    LOGGING["loggers"]["django"]["handlers"].append("rollbar")
    LOGGING["loggers"]["managr"]["handlers"].remove("mail_admins")
    LOGGING["loggers"]["managr"]["handlers"].append("rollbar")


#
# Nylas Integration Settings
#
USE_NYLAS = os.environ.get("USE_NYLAS") == "True"
if USE_NYLAS:
    NYLAS_CLIENT_ID = _env_get_required("NYLAS_CLIENT_ID")
    NYLAS_CLIENT_SECRET = _env_get_required("NYLAS_CLIENT_SECRET")
    NYLAS_OAUTH_CALLBACK_URL = _env_get_required("NYLAS_OAUTH_CALLBACK_URL")


#
# Twilio Integration Settings
#
USE_TWILIO = os.environ.get("USE_TWILIO") == "True"
if USE_TWILIO:
    TWILIO_ACCOUNT_SID = (
        _env_get_required("TWILIO_ACCOUNT_SID")
        if not IN_CI
        else os.environ.get("TWILIO_ACCOUNT_SID", "")
    )
    TWILIO_AUTH_TOKEN = (
        _env_get_required("TWILIO_AUTH_TOKEN")
        if not IN_CI
        else os.environ.get("TWILIO_AUTH_TOKEN", "")
    )
    TWILIO_BASE_CALLBACK_URL = (
        _env_get_required("TWILIO_BASE_CALLBACK_URL")
        if not IN_CI
        else os.environ.get("TWILIO_BASE_CALLBACK_URL", "")
    )

USE_ZOOM = os.environ.get("USE_ZOOM") == "True"
if USE_ZOOM:
    if IN_DEV:
        ZOOM_REDIRECT_URI = _env_get_required("ZOOM_REDIRECT_URI_DEV")
        ZOOM_CLIENT_ID = _env_get_required("ZOOM_CLIENT_ID_DEV")
        ZOOM_SECRET = _env_get_required("ZOOM_SECRET_DEV")
    elif IN_STAGING:
        ZOOM_REDIRECT_URI = _env_get_required("ZOOM_REDIRECT_URI_STAGING")
        ZOOM_CLIENT_ID = _env_get_required("ZOOM_CLIENT_ID_STAGING")
        ZOOM_SECRET = _env_get_required("ZOOM_SECRET_STAGING")
    elif IN_PROD:
        ZOOM_REDIRECT_URI = _env_get_required("ZOOM_REDIRECT_URI_PROD")
        ZOOM_CLIENT_ID = _env_get_required("ZOOM_CLIENT_ID_PROD")
        ZOOM_SECRET = _env_get_required("ZOOM_SECRET_PROD")
USE_SLACK = os.environ.get("USE_SLACK") == "True"
if USE_SLACK:
    SLACK_SECRET = _env_get_required("SLACK_SECRET")
    SLACK_CLIENT_ID = _env_get_required("SLACK_CLIENT_ID")

TEST_SLACK = os.environ.get("TEST_SLACK") == "True"
if USE_SLACK and TEST_SLACK:
    SLACK_TEST_TEAM_NAME = _env_get_required("SLACK_TEST_TEAM_NAME")
    SLACK_TEST_TEAM_ID = _env_get_required("SLACK_TEST_TEAM_ID")
    SLACK_TEST_BOT_USER_ID = _env_get_required("SLACK_TEST_BOT_USER_ID")
    SLACK_TEST_ACCESS_TOKEN = _env_get_required("SLACK_TEST_ACCESS_TOKEN")
    SLACK_TEST_INCOMING_WEBHOOK_URL = _env_get_required(
        "SLACK_TEST_INCOMING_WEBHOOK_URL"
    )
    SLACK_TEST_INCOMING_WEBHOOK_CHANNEL = _env_get_required(
        "SLACK_TEST_INCOMING_WEBHOOK_CHANNEL"
    )
    SLACK_TEST_INCOMING_WEBHOOK_CHANNEL_ID = _env_get_required(
        "SLACK_TEST_INCOMING_WEBHOOK_CHANNEL_ID"
    )
    SLACK_TEST_INCOMING_WEBHOOK_CONFIGURATION_URL = _env_get_required(
        "SLACK_TEST_INCOMING_WEBHOOK_CONFIGURATION_URL"
    )

