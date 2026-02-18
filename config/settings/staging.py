from .base import *

DEBUG = False

DJANGO_SETTINGS_MODULE = 'config.settings.staging'

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['dev.al-serag.net'])

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://alserag_user:STRONG_PASSWORD@127.0.0.1:5432/alserag_dev')
}
