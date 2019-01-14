import os

import environ
import raven
from django.utils.translation import ugettext_lazy as _

checkout_dir = environ.Path(__file__) - 2
assert os.path.exists(checkout_dir('manage.py'))

parent_dir = checkout_dir.path('..')
if os.path.isdir(parent_dir('etc')):
    env_file = parent_dir('etc/env')
    default_var_root = environ.Path(parent_dir('var'))
else:
    env_file = checkout_dir('.env')
    default_var_root = environ.Path(checkout_dir('var'))

env = environ.Env(
    DEBUG=(bool, False),
    TIER=(str, 'dev'),  # one of: prod, qa, stage, test, dev
    SECRET_KEY=(str, ''),
    MEDIA_ROOT=(environ.Path(), default_var_root('media')),
    STATIC_ROOT=(environ.Path(), default_var_root('static')),
    MEDIA_URL=(str, '/media/'),
    STATIC_URL=(str, '/static/'),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, 'postgis://haravajarjestelma:haravajarjestelma@localhost/haravajarjestelma'),
    CACHE_URL=(str, 'locmemcache://'),
    EMAIL_URL=(str, 'consolemail://'),
    SENTRY_DSN=(str, ''),
    CORS_ORIGIN_WHITELIST=(list, []),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
    NOTIFICATIONS_ENABLED=(bool, False),
    TOKEN_AUTH_ACCEPTED_AUDIENCE=(str, ''),
    TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=(str, ''),
    TOKEN_AUTH_AUTHSERVER_URL=(str, ''),
    TOKEN_AUTH_FIELD_FOR_CONSENTS=(str, ''),
    TOKEN_AUTH_REQUIRE_SCOPE_PREFIX=(bool, True),
)
if os.path.exists(env_file):
    env.read_env(env_file)

try:
    version = raven.fetch_git_sha(checkout_dir())
except Exception:
    version = None

BASE_DIR = str(checkout_dir)

DEBUG = env.bool('DEBUG')
TIER = env.str('TIER')
SECRET_KEY = env.str('SECRET_KEY')
if DEBUG and not SECRET_KEY:
    SECRET_KEY = 'xxx'

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {'default': env.db()}
# Ensure postgis engine
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

CACHES = {'default': env.cache()}
vars().update(env.email_url())  # EMAIL_BACKEND etc.
RAVEN_CONFIG = {'dsn': env.str('SENTRY_DSN'), 'release': version}

MEDIA_ROOT = env('MEDIA_ROOT')
STATIC_ROOT = env('STATIC_ROOT')
MEDIA_URL = env.str('MEDIA_URL')
STATIC_URL = env.str('STATIC_URL')

ROOT_URLCONF = 'haravajarjestelma.urls'
WSGI_APPLICATION = 'haravajarjestelma.wsgi.application'

LANGUAGE_CODE = 'fi'
LANGUAGES = (
    ('fi', _('Finnish')),
    ('en', _('English')),
    ('sv', _('Swedish'))
)
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

INSTALLED_APPS = [
    'helusers',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rest_framework_gis',
    'corsheaders',
    'munigeo',

    'events',
    'users',
    'areas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

SITE_ID = 1

AUTH_USER_MODEL = 'users.User'

DEFAULT_SRID = 4326

CORS_ORIGIN_WHITELIST = env('CORS_ORIGIN_WHITELIST')
CORS_ORIGIN_ALLOW_ALL = env('CORS_ORIGIN_ALLOW_ALL')

OIDC_API_TOKEN_AUTH = {
    'AUDIENCE': env.str('TOKEN_AUTH_ACCEPTED_AUDIENCE'),
    'API_SCOPE_PREFIX': env.str('TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX'),
    'ISSUER': env.str('TOKEN_AUTH_AUTHSERVER_URL'),
    'API_AUTHORIZATION_FIELD': env.str('TOKEN_AUTH_FIELD_FOR_CONSENTS'),
    'REQUIRE_API_SCOPE_FOR_AUTHENTICATION': env.bool('TOKEN_AUTH_REQUIRE_SCOPE_PREFIX'),
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': ('helusers.oidc.ApiTokenAuthentication',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# local_settings.py can be used to override settings
local_settings_path = os.path.join(checkout_dir(), "local_settings.py")
if os.path.exists(local_settings_path):
    with open(local_settings_path) as fp:
        code = compile(fp.read(), local_settings_path, 'exec')
    exec(code, globals(), locals())
