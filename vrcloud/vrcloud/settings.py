"""
This file generated from the template at configuration/template.settings.py
For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/

Environment Variables:
IMAGE_NAME          - the name of the image running this code
HOME                - the home directory of the user running this code
DJANGO_ADMIN_NAME   - the name of the primary admin
DJANGO_ADMIN_EMAIL  - the e-mail address of the primary admin
DJANGO_SECRET_KEY   - some large lump of very secret, very random content
DJANGO_PRODUCTION   - True if prod, False otherwise
REDIS_LOCATION      - e.g. '/tmp/redis.sock' or '<host>:<port>'

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

VERBOSE = os.environ.get("DJANGO_VERBOSE", True)

HOME_DIR = os.environ.get("HOME")
if VERBOSE:
    print("HOME: {}".format(HOME_DIR))

ADMINS = ((os.environ.get("DJANGO_ADMIN_NAME", "Curtis Lassam"),
           os.environ.get("DJANGO_ADMIN_EMAIL", "curtis@lassam.net")), )
if VERBOSE:
    print("ADMINS: {}".format(ADMINS))

SITE_DOMAIN = os.environ.get("DJANGO_DOMAIN", "marquee.click")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", uuid.uuid4())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not os.environ.get("DJANGO_PRODUCTION", False)

if DEBUG and VERBOSE:
    print("Loading in DEBUG mode!")
elif VERBOSE:
    print("Loading in PRODUCTION mode!")

ALLOWED_HOSTS = ['*']

if DEBUG:
    # When we're in debug mode, we don't want any caching to occur
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }
else:
    # TODO: MessagePack here, instead of the default Pickle
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': os.environ.get("REDIS_LOCATION", '/tmp/redis.sock')
        },
    }
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 60 * 60

# CELERY SETTINGS
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

ROOT_URLCONF = 'vrcloud.urls'

WSGI_APPLICATION = 'vrcloud.wsgi.application'

# Database
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

if DEBUG:
    SITE_URL = 'http://localhost:18080'
else:
    SITE_URL = "http://{}".format(SITE_DOMAIN)

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

STATIC_URL = '/static/'
STATIC_ROOT = '${HOME}/static'

MEDIA_URL = SITE_URL + '/media/'
MEDIA_ROOT = '${HOME}/media'

# AUTH STUFF
LOGIN_URL = "/dashboard/login"

# TZ
TIME_ZONE = 'America/Vancouver'
USE_TZ = True

FAVICON = ''
SITE_TITLE = 'VR Cloud'
SITE_META = 'words go here'

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
            ],
        },
    },
]

CELERYBEAT_SCHEDULE = {
}
