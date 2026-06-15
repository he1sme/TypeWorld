from pathlib import Path

import os

try:

    from dotenv import load_dotenv

except ImportError:

    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent

if load_dotenv:

    load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get('TYPEWORLD_SECRET_KEY', 'typeworld-dev-secret-key')

DEBUG = os.environ.get('TYPEWORLD_DEBUG', '1') == '1'

ALLOWED_HOSTS = os.environ.get('TYPEWORLD_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [

    'daphne',

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.sites',

    'django.contrib.staticfiles',

    'channels',

    'allauth',

    'allauth.account',

    'allauth.socialaccount',

    'allauth.socialaccount.providers.google',

    'allauth.socialaccount.providers.vk',

    'races',

]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'allauth.account.middleware.AccountMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'typeworld.urls'

TEMPLATES = [

    {

        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.debug',

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

                'races.context_processors.typeworld_auth',

            ],

        },

    },

]

WSGI_APPLICATION = 'typeworld.wsgi.application'

ASGI_APPLICATION = 'typeworld.asgi.application'

CHANNEL_LAYERS = {

    'default': {

        'BACKEND': 'channels.layers.InMemoryChannelLayer'

    }

}

DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': BASE_DIR / 'db.sqlite3',

    }

}

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/'

                          

SITE_ID = 1

AUTHENTICATION_BACKENDS = [

    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',

]

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/profile/'

LOGOUT_REDIRECT_URL = '/'

ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_LOGIN_METHODS = {'username', 'email'}

ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*']

SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_ADAPTER = 'races.social_adapter.TypeWorldSocialAdapter'

SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_PROVIDERS = {

    'google': {

        'SCOPE': ['profile', 'email'],

        'AUTH_PARAMS': {'access_type': 'online'},

    },

    'vk': {

        'SCOPE': ['email'],

    },

}

                                                                         

                                                                                 

EMAIL_BACKEND = os.environ.get('TYPEWORLD_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

EMAIL_HOST = os.environ.get('TYPEWORLD_EMAIL_HOST', 'smtp.gmail.com')

EMAIL_PORT = int(os.environ.get('TYPEWORLD_EMAIL_PORT', '587'))

EMAIL_HOST_USER = os.environ.get('TYPEWORLD_EMAIL_HOST_USER', '')

EMAIL_HOST_PASSWORD = os.environ.get('TYPEWORLD_EMAIL_HOST_PASSWORD', '')

EMAIL_USE_TLS = os.environ.get('TYPEWORLD_EMAIL_USE_TLS', '1') == '1'

DEFAULT_FROM_EMAIL = os.environ.get('TYPEWORLD_DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'TypeWorld <noreply@typeworld.local>')
