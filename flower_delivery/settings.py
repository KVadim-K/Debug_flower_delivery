# settings.py

from pathlib import Path
import os
import logging.config
from dotenv import load_dotenv

# Определение BASE_DIR для поиска .env
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR.parent / '.env'

# Загрузка переменных окружения
# load_dotenv(dotenv_path=env_path)

# Переменные для основного бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = os.getenv('API_URL')
SITE_URL = os.getenv('SITE_URL')
TELEGRAM_IDS_RAW = os.getenv('TELEGRAM_IDS', '')
TELEGRAM_IDS = [int(id.strip()) for id in TELEGRAM_IDS_RAW.split(',') if id.strip().isdigit()]

# Переменные для административного бота
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN')
ADMIN_TELEGRAM_IDS_RAW = os.getenv('ADMIN_TELEGRAM_IDS', '')
ADMIN_TELEGRAM_IDS = [int(id.strip()) for id in ADMIN_TELEGRAM_IDS_RAW.split(',') if id.strip().isdigit()]
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv('DEBUG', 0)))

# Указываем, что запросы через прокси (например, Nginx) используют HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ALLOWED_HOSTS: загрузка из переменной окружения .env
ALLOWED_HOSTS = list(
    filter(
        lambda host: host,
        map(
            lambda host: host.strip(),
            os.getenv('ALLOWED_HOSTS', 'localhost,').split(',')
        )
    )
)

# CSRF_TRUSTED_ORIGINS: доверенные источники для CSRF
CSRF_TRUSTED_ORIGINS = [
    f'http://{host}' for host in ALLOWED_HOSTS
] + [
    f'https://{host}' for host in ALLOWED_HOSTS
]

# CORS_ALLOWED_ORIGINS: разрешенные источники для CORS
CORS_ALLOWED_ORIGINS = [
    f'http://{host}' for host in ALLOWED_HOSTS
] + [
    f'https://{host}' for host in ALLOWED_HOSTS
]


# Application definition

INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_celery_results',

    # Необходимо для django-allauth
    'django.contrib.sites',

    # Сторонние приложения
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Другие сторонние приложения (например, для аналитики)
    'rest_framework',
    'rest_framework.authtoken',
    'social_django',

    # Ваши приложения
    'users.apps.UsersConfig',
    'products.apps.ProductsConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'reviews.apps.ReviewsConfig',
    'reports.apps.ReportsConfig',
    'telegram_bot',  # Добавляем telegram_bot
    'telegramadmin_bot',   # Новый админ-бот
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Добавлено здесь
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'flower_delivery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Создайте папку templates в корне проекта
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Необходимо для django-allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'flower_delivery.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'  # Для московского времени

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.CustomUser'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

FAVICON_PATH = STATIC_URL + 'img/favicon.ico'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Стандартный бэкенд Django
    'allauth.account.auth_backends.AuthenticationBackend',  # Бэкенд для django-allauth
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.telegram.TelegramAuth',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


SITE_ID = 1

# Django Allauth Settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # 'none', 'mandatory', 'optional'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_FROM_EMAIL = 'd3liveryflower@yandex.ru'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False  # Не включайте одновременно SSL и TLS
EMAIL_HOST_USER = 'd3liveryflower@yandex.ru'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Настройки для Celery
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

# Настройки URL
SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['state']
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_CHECK_STATE = True  # Включаем проверку state


# Загрузка ключей и секретов из .env файла
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'https://vaktest.ru/oauth/complete/google-oauth2/'

SOCIAL_AUTH_VK_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_VK_OAUTH2_KEY')
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_VK_OAUTH2_SECRET')
SOCIAL_AUTH_VK_OAUTH2_REDIRECT_URI = os.getenv('SOCIAL_AUTH_VK_OAUTH2_REDIRECT_URI')

SOCIAL_AUTH_GITHUB_KEY = os.getenv('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.getenv('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_GITHUB_OAUTH2_REDIRECT_URI = os.getenv('SOCIAL_AUTH_GITHUB_OAUTH2_REDIRECT_URI')

SOCIAL_AUTH_TELEGRAM_BOT_TOKEN = os.getenv('SOCIAL_AUTH_TELEGRAM_BOT_TOKEN')

SOCIAL_AUTH_TELEGRAM_REDIRECT_URL = "https://vaktest.ru/oauth/complete/telegram/"

# Другие настройки
SOCIAL_AUTH_PIPELINE = (
#    'users.utils.pipeline_debug_step',
#    'users.utils.early_test_pipeline_step',
#    'users.utils.test_pipeline_step',  # Тестовый шаг
#    'users.utils.log_state',  # Новый шаг для логирования
#    'users.utils.debug_state',
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
#    'users.utils.generate_fake_email',  # ваш кастомный шаг
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'users.utils.log_pipeline_step',  # Логирование перед create_user
#    'users.utils.create_user_with_logging',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
#    'users.utils.log_access_token',  # Заменили path.to.log_access_token
    'social_core.pipeline.user.user_details',
)


# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 недели
SESSION_COOKIE_NAME = "flowerdelivery_session"
SESSION_COOKIE_SECURE = True  # Куки только через HTTPS
SESSION_COOKIE_HTTPONLY = True  # Доступ к куки только серверу
SESSION_COOKIE_SAMESITE = 'None'  # Защита от атак типа CSRF
SESSION_COOKIE_DOMAIN = ".vaktest.ru"  # Поддержка www.vaktest.ru

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CORS_ALLOW_CREDENTIALS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'users.utils': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'social': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'social.backends': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.contrib.sessions': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'social_core.backends': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# # Загрузка переменных окружения
# print(f"API_URL from settings: {API_URL}")
# print(f"ADMIN_TELEGRAM_IDS from settings: {ADMIN_TELEGRAM_IDS}")

# print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
# print(f"DEBUG: {DEBUG}")
# print(f"Loaded ALLOWED_HOSTS from .env: {os.getenv('ALLOWED_HOSTS')}")
# print("DEBUG: generate_fake_email called")
