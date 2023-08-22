import os
import dj_database_url
import requests
from managr.utils import sites as site_utils


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
    SERVER_EMAIL = "Managr Support <support@mg.managr.ai>"
elif IN_STAGING:
    SERVER_EMAIL = "Managr <no-reply-staging@managr.ai>"
else:
    SERVER_EMAIL = "Managr <no-reply@mg.managr.ai>"

DEFAULT_FROM_EMAIL = SERVER_EMAIL

# Email address of the staff who should receive certain emails
STAFF_EMAIL = _env_get_required("STAFF_EMAIL")

#
# Domain Configuration
#
CURRENT_DOMAIN = _env_get_required("CURRENT_DOMAIN")
CURRENT_PORT = os.environ.get("CURRENT_PORT")
ALLOWED_HOSTS = []
# METADATA_URI = os.environ.get("ECS_CONTAINER_METADATA_URI", [])
# container_metadata = requests.get(METADATA_URI).json()
# ALLOWED_HOSTS.append(container_metadata["Networks"][0]["IPv4Addresses"][0])
ALLOWED_HOSTS += _env_get_required("ALLOWED_HOSTS").split(",")

# print(ALLOWED_HOSTS)
### Get allowed hosts from ecs

EC2_PRIVATE_IP = None
METADATA_URI = os.environ.get("ECS_CONTAINER_METADATA_URI_V4", None)

try:
    resp = requests.get(METADATA_URI)
    data = resp.json()

    EC2_PRIVATE_IP = data["Networks"][0]["IPv4Addresses"][0]
except Exception as e:
    # silently fail as we may not be in an ECS environment
    pass

if EC2_PRIVATE_IP:
    # Be sure your ALLOWED_HOSTS is a list NOT a tuple
    # or .append() will fail
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)

if CURRENT_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(CURRENT_DOMAIN)

# Application definition

INSTALLED_APPS = [
    # Django Channels
    "channels",
    # Local
    "managr.core",
    "managr.api",
    "managr.opportunity",
    "managr.organization",
    # "managr.report",
    "managr.slack",
    "managr.zoom",
    "managr.salesforce",
    "managr.alerts",
    "managr.autonomous",
    "managr.salesloft",
    "managr.gong",
    "managr.outreach",
    "managr.hubspot",
    "managr.meetings",
    "managr.crm",
    "managr.comms",
    # "managr.demo",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 'django_eventstream',
    # Third Party
    "django_nose",
    "storages",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "django_extensions",
    "background_task",
    "kronos",
    # "django_otp",
    # "django_otp.plugins.otp_totp",
]

# EVENTSTREAM_STORE_CLASS = 'django_eventstream.stores.DjangoModelStore'
# EVENTSTREAM_STORE = 'django_eventstream.stores.redis.RedisEventStore'

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "managr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "../client/dist/"),
            os.path.join(BASE_DIR, "managr", "salesforce", "templates", ""),
            os.path.join(BASE_DIR, "managr", "core", "templates", ""),
            os.path.join(BASE_DIR, "managr", "api", "templates", ""),
        ],
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

# Channels
ASGI_APPLICATION = "managr.routing.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            # 'hosts': [('127.0.0.1', 6379)],
            "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379")],
            "capacity": 500,
        },
    },
}

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
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
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
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "managr.api.models.ExpiringTokenAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

AUTHENTICATION_BACKENDS = [
    "managr.api.models.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]
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
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
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
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        # The logger name matters -- it MUST match the name of the app
        "managr": {
            "handlers": [
                "console",
                "mail_admins",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
        "managr.request": {"handlers": [], "level": "INFO", "propagate": True},
        "managr.tasks": {"handlers": [], "level": "INFO", "propagate": True},
    },
}

# Popular testing framework that allows logging to stdout while running unit tests
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

# Shows stdout when running tests.
NOSE_ARGS = [
    "--nocapture",
    "--nologcapture",
]


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
    ZOOM_REDIRECT_URI = _env_get_required("ZOOM_REDIRECT_URI")
    ZOOM_CLIENT_ID = _env_get_required("ZOOM_CLIENT_ID")
    ZOOM_SECRET = _env_get_required("ZOOM_SECRET")
    ZOOM_WEBHOOK_TOKEN = _env_get_required("ZOOM_WEBHOOK_TOKEN")
    ZOOM_FAKE_MEETING_UUID = os.environ.get("ZOOM_FAKE_MEETING_UUID", None)


USE_SLACK = os.environ.get("USE_SLACK") == "True"
if USE_SLACK:
    SLACK_SECRET = _env_get_required("SLACK_SECRET")
    SLACK_CLIENT_ID = _env_get_required("SLACK_CLIENT_ID")
    SLACK_SIGNING_SECRET = _env_get_required("SLACK_SIGNING_SECRET")
    SLACK_APP_VERSION = _env_get_required("SLACK_APP_VERSION")
    SLACK_ERROR_WEBHOOK = (
        os.environ.get("SLACK_ERROR_WEBHOOK", None)
        if os.environ.get("SLACK_ERROR_WEBHOOK") not in ["", None]
        else None
    )


USE_SALESFORCE = os.environ.get("USE_SALESFORCE") == "True"
if USE_SALESFORCE:
    SALESFORCE_SECRET = _env_get_required("SALESFORCE_SECRET")
    SALESFORCE_CONSUMER_KEY = _env_get_required("SALESFORCE_CONSUMER_KEY")
    SALESFORCE_BASE_URL = _env_get_required("SALESFORCE_BASE_URL")
    SALESFORCE_SCOPES = _env_get_required("SALESFORCE_SCOPES")
    SALESFORCE_REDIRECT_URL = _env_get_required("SALESFORCE_REDIRECT_URI")
    # SALESFORCE_REDIRECT_URL = (
    #    f'http://localhost:8080/{_env_get_required("SALESFORCE_REDIRECT_URI")}'
    #    if IN_DEV
    #    else f'{site_utils.get_site_url()}/{_env_get_required("SALESFORCE_REDIRECT_URI")}'
    # )
    SALESFORCE_API_VERSION = f'v{_env_get_required("SALESFORCE_API_VERSION")}'


USE_SALESLOFT = os.environ.get("USE_SALESLOFT") == "True"
if USE_SALESLOFT:
    SALESLOFT_SECRET = _env_get_required("SALESLOFT_SECRET")
    SALESLOFT_CLIENT_ID = _env_get_required("SALESLOFT_CLIENT_ID")
    SALESLOFT_BASE_URL = _env_get_required("SALESLOFT_BASE_URL")
    SALESLOFT_REDIRECT_URI = _env_get_required("SALESLOFT_REDIRECT_URI")

USE_OUTREACH = os.environ.get("USE_OUTREACH") == "True"
if USE_OUTREACH:
    OUTREACH_SECRET = _env_get_required("OUTREACH_SECRET")
    OUTREACH_CLIENT_ID = _env_get_required("OUTREACH_CLIENT_ID")
    OUTREACH_BASE_URL = _env_get_required("OUTREACH_BASE_URL")
    OUTREACH_REDIRECT_URI = _env_get_required("OUTREACH_REDIRECT_URI")

USE_GONG = os.environ.get("USE_GONG") == "True"
if USE_GONG:
    GONG_SECRET = _env_get_required("GONG_SECRET")
    GONG_CLIENT_ID = _env_get_required("GONG_CLIENT_ID")
    GONG_BASE_URL = _env_get_required("GONG_BASE_URL")
    GONG_REDIRECT_URI = _env_get_required("GONG_REDIRECT_URI")

USE_HUBSPOT = os.environ.get("USE_HUBSPOT") == "True"
if USE_HUBSPOT:
    HUBSPOT_SECRET = _env_get_required("HUBSPOT_SECRET")
    HUBSPOT_CLIENT_ID = _env_get_required("HUBSPOT_CLIENT_ID")
    HUBSPOT_BASE_URL = _env_get_required("HUBSPOT_BASE_URL")
    HUBSPOT_REDIRECT_URI = _env_get_required("HUBSPOT_REDIRECT_URI")

USE_OPEN_AI = os.environ.get("USE_OPEN_AI") == "True"
if USE_OPEN_AI:
    OPEN_AI_SECRET = _env_get_required("OPEN_AI_SECRET")

USE_SSO = os.environ.get("USE_SSO") == "True"
if USE_SSO:
    MICROSOFT_SECURITY_KEY = _env_get_required("MICROSOFT_SECRET_KEY")
    GOOGLE_CLIENT_ID = _env_get_required("GOOGLE_CLIENT_ID")
    GOOGLE_LOGIN_URI = _env_get_required("GOOGLE_LOGIN_URI")

USE_NEWS_API = os.environ.get("USE_NEWS_API") == "True"
if USE_NEWS_API:
    NEWS_API_KEY = _env_get_required("NEWS_API_KEY")

USE_TWITTER_API = os.environ.get("USE_TWITTER_API") == "True"
if USE_TWITTER_API:
    TWITTER_ACCESS_TOKEN = _env_get_required("TWITTER_ACCESS_TOKEN")
    TWITTER_CLIENT_ID = _env_get_required("TWITTER_CLIENT_ID")
    TWITTER_REDIRECT_URI = _env_get_required("TWITTER_REDIRECT_URI")

MAX_ATTEMPTS = 5
