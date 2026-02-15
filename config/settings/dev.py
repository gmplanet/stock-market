from .base import *

# Включаем режим отладки локально
DEBUG = True

ALLOWED_HOSTS = ['*']

# База данных для разработки (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Вывод email в консоль (вместо отправки)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Панель отладки (если установлена в requirements/dev.txt)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass
