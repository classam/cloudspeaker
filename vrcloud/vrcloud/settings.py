"""
This file generated from the template at configuration/template.settings.py
For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/

Environment Variables:

HOME                    - the home directory of the user running this code

DJANGO_ADMIN_NAME       - the name of the primary admin
DJANGO_ADMIN_EMAIL      - the e-mail address of the primary admin
DJANGO_SECRET_KEY       - some large lump of very secret, very random content
DJANGO_PRODUCTION       - True if prod, False otherwise
DJANGO_DOMAIN           - The domain this site is being served from (i.e. 'butts.com')
DJANGO_STATIC_URL       - URL where static site assets (js, css) are served from.
DJANGO_STATIC_ROOT      - Location of static site assets
DJANGO_MEDIA_URL        - URL where media (user files) are served from.
DJANGO_MEDIA_ROOT       - Location of media files.
DJANGO_FAVICON          - Location of a favicon

GOOGLE_ANALYTICS_TOKEN  - Google Analytics account name - like "UA-41279849-1"

POSTGRES_HOST           -
POSTGRES_PORT           -
POSTGRES_DB             -
POSTGRES_USER           -
POSTGRES_PASSWORD       -

RABBITMQ_HOST           -
RABBITMQ_PORT           -
RABBITMQ_USER           -
RABBITMQ_PASS           -

REDIS_LOCATION          - e.g. '/tmp/redis.sock' or '<host>:<port>'

AWS_ACCESS_KEY_ID       - Needed for SES Email.
AWS_SECRET_ACCESS_KEY   -
AWS_SES_REGION_NAME     - The AWS region we're serving e-mail from - like "us-west-2"

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import uuid
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

VERBOSE = os.environ.get("DJANGO_VERBOSE", True)

HOME_DIR = os.environ.get("HOME")
if VERBOSE:
    print("HOME: {}".format(HOME_DIR))

ADMINS = ((os.environ.get("DJANGO_ADMIN_NAME", "Curtis Lassam"),
           os.environ.get("DJANGO_ADMIN_EMAIL", "curtis@lassam.net")), )
if VERBOSE:
    print("ADMINS: {}".format(ADMINS))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", uuid.uuid4())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not os.environ.get("DJANGO_PRODUCTION", False)

if DEBUG and VERBOSE:
    print("Loading in DEBUG mode!")
elif VERBOSE:
    print("Loading in PRODUCTION mode!")

ALLOWED_HOSTS = ['*']

# DATABASE CONFIGURATIONS!
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'cloudspeaker'),
        'USER': os.environ.get('POSTGRES_USER', 'cloudspeaker'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'cloudspeaker'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# CACHE CONFIGURATIONS
# https://docs.djangoproject.com/en/1.9/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get("REDIS_LOCATION", 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'data': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get("REDIS_LOCATION", 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.msgpack.MSGPackSerializer',
        }
    },
}
CACHE_MIDDLEWARE_ALIAS = 'default'

if DEBUG:
    CACHE_MIDDLEWARE_SECONDS = 1
else:
    CACHE_MIDDLEWARE_SECONDS = 60

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# CELERY SETTINGS
# http://docs.celeryproject.org/en/latest/django/index.html
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', '5432')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'rabbityface')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASSWORD', 'rabbitypass')
BROKER_URL = 'amqp://{user}:{passwd}@{host}:{port}//'.format(host=RABBITMQ_HOST,
                                                             port=RABBITMQ_PORT,
                                                             user=RABBITMQ_USER,
                                                             passwd=RABBITMQ_PASS)

# TODO: MsgPack
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# URL

SITE_DOMAIN = os.environ.get("DJANGO_DOMAIN", "marquee.click")

ROOT_URLCONF = 'vrcloud.urls'
WSGI_APPLICATION = 'vrcloud.wsgi.application'

if DEBUG:
    SITE_URL = 'http://localhost:8080'
else:
    SITE_URL = "http://{}".format(SITE_DOMAIN)

# Email
# https://github.com/django-ses/django-ses

EMAIL_SUBJECT_PREFIX = 'VR Cloud '
SERVER_EMAIL = os.environ.get("DJANGO_ADMIN_EMAIL", "curtis@lassam.net")
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
    AWS_SES_REGION_NAME = os.environ.get("AWS_SES_REGION_NAME", 'us-west-2')
    AWS_SES_REGION_ENDPOINT = '{}.amazonaws.com'.format(AWS_SES_REGION_NAME)

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = False

USE_L10N = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# Everything that matches the STATIC_URL will be served from the STATIC_ROOT
# This is for css, javascript, and images.
STATIC_URL = os.environ.get('DJANGO_STATIC_URL', '/static/')
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT', '/tmp/static')

# Everything that matches the MEDIA_URL will be served from the MEDIA_ROOT
# This is for user-uploaded files.
MEDIA_URL = os.environ.get('DJANGO_MEDIA_URL', SITE_URL + '/media/')
MEDIA_ROOT = os.environ.get('DJANGO_MEDIA_ROOT', '/tmp/media')

# TZ
TIME_ZONE = 'America/Vancouver'
USE_TZ = True

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ses',
    'bootstrap3',

    'status',
    'dashboard',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(module)s :  %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True
        },
        'vrcloud':{
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True
        }
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context.globalsettings'
            ],
        },
    },
]

CELERYBEAT_SCHEDULE = {
    'celerystatus':{
        'task':'status.tasks.tick',
            'schedule': timedelta(minutes=1),
    },
}

# Authentication
# https://django-registration.readthedocs.org/en/2.0.3/
LOGIN_URL = "/dashboard/login"
ACCOUNT_ACTIVATION_DAYS = 7

# Master Template Stuff
GOOGLE_ANALYTICS_TOKEN = os.environ.get('GOOGLE_ANALYTICS_TOKEN', '12345')
FAVICON = os.environ.get('DJANGO_FAVICON', 'http://cube-drone.com/static/dashboard/images/favicon.png')
SITE_TITLE = os.environ.get('DJANGO_SITE_TITLE', 'MCClick')
SITE_META = os.environ.get('DJANGO_SITE_META', 'An online community for things and stuff.')
