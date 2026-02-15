from pathlib import Path
import os
import environ

# Инициализация environ
env = environ.Env()
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))

# Путь к корню проекта (stock-market/)
# config/settings/base.py -> config/settings/ -> config/ -> stock-market/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# БЕЗОПАСНОСТЬ: Ключ должен быть в .env
SECRET_KEY = env('SECRET_KEY', default='django-insecure-unsafe-key-for-dev')

# Приложения
INSTALLED_APPS = [
    # Admin Interface (должен быть перед admin)
    'admin_interface',
    'colorfield',

    # Стандартные приложения
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # === БЛОК ALLAUTH===
    'django.contrib.sites',      # Обязательно для allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Провайдер Google
    # ==========================

    # Сторонние библиотеки (Фаза 0 и 1)
    'parler',      # Мультиязычность
    
    # Наши приложения (создадим их структуру сейчас)
    'apps.core',
    'apps.accounts',
    'apps.catalog',
    'apps.warehouse',
    
    # Сторонние библиотеки
  
    'django_ckeditor_5',
    
    'mptt',       # <--- ВОТ ЭТА СТРОКА ОБЯЗАТЕЛЬНА!
    'imagekit',
    'django_cleanup.apps.CleanupConfig',
    'apps.orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # <--- ВАЖНО: для перевода
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Папка для общих шаблонов
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Наш кастомный процессор (создадим позже)
                # 'apps.core.context_processors.site_settings', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Интернационализация (I18N)
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Список языков
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Español'),
    ('ru', 'Русский'),
]

# Папка с переводами
LOCALE_PATHS = [BASE_DIR / 'locale']

# Настройки Django-Parler
PARLER_LANGUAGES = {
    None: (
        {'code': 'en'},
        {'code': 'es'},
        {'code': 'ru'},
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}

# Статика и Медиа
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Кастомная модель пользователя (Фаза 2)
AUTH_USER_MODEL = 'accounts.User'

# ID сайта (понадобится для allauth)
SITE_ID = 1

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# === Allauth Configuration ===
SITE_ID = 1  # Очень важно!

# Указываем, какие бэкенды аутентификации использовать
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',     # Стандартный вход (админка)
    'allauth.account.auth_backends.AuthenticationBackend',  # Вход через email/соцсети
]

# Настройки поведения
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Вход только по Email
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False        # Юзернейм не нужен
ACCOUNT_USER_MODEL_USERNAME_FIELD = None # Убираем поле username из формы
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Подтверждение почты (пока необязательно)
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False  # Пароль при регистрации 1 раз
ACCOUNT_SESSION_REMEMBER = True          # "Запомнить меня" по умолчанию
ACCOUNT_UNIQUE_EMAIL = True

# Куда перенаправлять после входа/выхода
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'



# === CKEditor 5 Configuration ===
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': 'custom',
                'backgroundColors': 'custom'
            },
            'tableCellProperties': {
                'borderColors': 'custom',
                'backgroundColors': 'custom'
            }
        },
        'heading': {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

