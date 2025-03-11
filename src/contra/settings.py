"""
Django settings for contra project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from decouple import config, Csv

# Configuração para usar PyMySQL como driver MySQL
import pymysql
pymysql.install_as_MySQLdb()

# Debug de variáveis de ambiente para verificar a configuração no Vercel
print("=== ENVIRONMENT VARIABLES ===")
print(f"USE_MYSQL: {config('USE_MYSQL', default=False)}")
print(f"MYSQL_DATABASE: {config('MYSQL_DATABASE', default='not-set')}")
print(f"MYSQL_HOST: {config('MYSQL_HOST', default='not-set')}")
print(f"MYSQL_USER: {config('MYSQL_USER', default='not-set')}")
print(f"DISABLE_DATABASE: {config('DISABLE_DATABASE', default=False)}")
print("===========================")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-91@r8e!+2*)^ry403*&8$4m@a0^_=an+7vfp3c*335bq1v1%n-')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Definir VERCEL como True se estivermos no ambiente Vercel
VERCEL = config('VERCEL', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

# Para ambiente Vercel, aceitamos qualquer host
if VERCEL:
    ALLOWED_HOSTS = ['*', '.vercel.app', '.thulio.tech']


# Application definition

INSTALLED_APPS = [
    'account.apps.AccountConfig', # poderia ser apenas 'account'
    'client.apps.ClientConfig', # poderia ser apenas 'client'
    'writer.apps.WriterConfig', # poderia ser apenas 'writer'
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_bootstrap5',
    'crispy_forms',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

AUTH_USER_MODEL = 'account.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'contra.middleware.DatabaseFixMiddleware',  # Middleware para corrigir o banco de dados
    'contra.middleware.SessionManagementMiddleware',  # Middleware para gerenciar sessões
]

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

ROOT_URLCONF = 'contra.urls'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'common' / 'templates' ],
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

WSGI_APPLICATION = 'contra.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Configurações de banco de dados
USE_MYSQL = config('USE_MYSQL', default=False, cast=bool)

# Configuração de bancos de dados
if USE_MYSQL:
    print("Usando banco de dados MySQL")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('MYSQL_DATABASE'),
            'USER': config('MYSQL_USER'),
            'PASSWORD': config('MYSQL_PASSWORD'),
            'HOST': config('MYSQL_HOST'),
            'PORT': config('MYSQL_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'use_unicode': True,
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'connect_timeout': 60,
            },
            'CONN_MAX_AGE': 60,
            'CONN_HEALTH_CHECKS': True,
        }
    }
else:
    print("Usando banco de dados SQLite")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3') if VERCEL else BASE_DIR / 'db.sqlite3',
        }
    }

# Debug extra para verificar o banco de dados
print(f"Database engine: {DATABASES['default']['ENGINE']}")
print(f"Database name: {DATABASES['default']['NAME']}")
print(f"Database host: {DATABASES['default'].get('HOST', 'local')}")


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Configuração específica para o Vercel
if VERCEL:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
    # Use WhiteNoise para servir arquivos estáticos no Vercel
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


########## PAYPAL SETTINGS ##########

PAYPAL_CLIENT_ID : str = config('PAYPAL_CLIENT_ID')
PAYPAL_SECRET_ID : str = config('PAYPAL_SECRET_ID')
PAYPAL_AUTH_URL : str = config('PAYPAL_AUTH_URL')
PAYPAL_BILLING_SUBSCRIPTIONS_URL: str = config('PAYPAL_BILLING_SUBSCRIPTIONS_URL')

########## SESSION SETTINGS ##########

# Configurações de sessão para melhorar a segurança
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)  # Cookies apenas via HTTPS
SESSION_COOKIE_HTTPONLY = True  # Cookies não acessíveis via JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'  # Proteção contra CSRF em navegadores modernos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Sessão expira ao fechar o navegador
SESSION_COOKIE_AGE = 3600  # Sessão expira após 1 hora de inatividade (em segundos)

# Configuração para armazenamento de sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Armazenar sessões no banco de dados
SESSION_SAVE_EVERY_REQUEST = True  # Atualizar o cookie de sessão a cada requisição