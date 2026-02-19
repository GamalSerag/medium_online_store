from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['al-serag.store', 'www.al-serag.store', 'dev.al-serag.store'])

# REQUIRED in production
DATABASE_URL = env('DATABASE_URL')  # will raise error if missing
DATABASES = {
    'default': env.db('DATABASE_URL'),
}
