# Core/settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- SECURITY SETTINGS ---
# SECURITY WARNING: keep the secret key used in production secret!
# For development, this is fine. For production, you should load this from an environment variable.
SECRET_KEY = 'kaberamaido-uganda@256'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# --- APPLICATION DEFINITION ---
# These are the applications that are included in your project.
# We have added the apps we plan to build: 'Users', 'Assets', and 'Incidents'.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our custom applications
    'users.apps.UsersConfig',
    'assets.apps.AssetsConfig',
    #'Incidents.apps.IncidentsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This tells Django where to find the main URL configuration for the project.
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # This tells Django to look for a 'templates' directory at the project's root level.
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'


# --- DATABASE CONFIGURATION ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# For development, we'll use SQLite, which is a simple file-based database.
# For production, you would typically use a more robust database like PostgreSQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- AUTHENTICATION & AUTHORIZATION ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
# This is the most important setting for our custom user model.
# It tells Django to use the 'CustomUser' model from our 'Users' app for all authentication purposes.
AUTH_USER_MODEL = 'users.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- INTERNATIONALIZATION ---
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'

# Based on your location, setting the time zone to Kampala.
TIME_ZONE = 'Africa/Kampala'

USE_I18N = True

USE_TZ = True


# --- STATIC AND MEDIA FILES ---
# https://docs.djangoproject.com/en/4.2/howto/static-files/
# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = '/static/'
# This is where Django's 'collectstatic' command will gather all static files for production.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# This tells Django to look for a 'static' directory at the project's root level for additional static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = '/media/'
# This is the directory where user-uploaded files (like profile photos) will be stored.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- DEFAULT PRIMARY KEY FIELD TYPE ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

