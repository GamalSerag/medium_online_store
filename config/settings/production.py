    from .base import *

DEBUG = False

DJANGO_SETTINGS_MODULE = 'config.settings.production'

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['al-serag.net', 'www.al-serag.net'])

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://alserag_user:STRONG_PASSWORD@127.0.0.1:5432/alserag_prod')
}
