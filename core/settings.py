"""
Django settings for Bulleo project.
Located at: core/settings.py
"""

from decouple import config
from pathlib import Path
from celery.schedules import crontab
import os
import dj_database_url
import sys
import cloudinary
import cloudinary.uploader
import cloudinary.api  # noqa: F401


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

DJANGO_ENV = config("DJANGO_ENV", default="development")

if DJANGO_ENV == "production":
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS", default=""
    ).split(",")
else:
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS", default="localhost,127.0.0.1"
    ).split(",")

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_celery_beat',
    'cloudinary',
    'cloudinary_storage',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'apps.users.apps.UsersConfig',
    'apps.news.apps.NewsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.auth_forms',
                'core.context_processors.notifications_unread_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600,
                                         ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

JAZZMIN_SETTINGS = {
    "site_title": "Bulleo Admin",
    "site_logo": "images/bulleo-admin-logo.png",
    "site_logo_classes": "img-circle",
    "site_logo_height": "40px",
    "custom_css": "css/admin-custom.css",
    "site_header": "Bulleo Administration",
    "site_brand": "Bulleo",
    "welcome_sign": "Welcome to Bulleo Admin Panel",
    "copyright": "Bulleo",

    "order_with_respect_to": [
        "users.Comment",
        "users.Notification",
        "users.Profile",
    ],

    "custom_links": {
        "news": [
            {
                "name": "Manage Articles",
                "url": "/admin/news/article/",
                "icon": "fas fa-newspaper",
                "permissions": ["news.view_article"]
            },
            {
                "name": "View Categories",
                "url": "/admin/news/category/",
                "icon": "fas fa-tags",
                "permissions": ["news.view_category"]
            },
        ],
        "users": [
            {
                "name": "Moderate Comments",
                "url": "/admin/users/comment/",
                "icon": "fas fa-comment-dots",
                "permissions": ["users.view_comment"]
            },
            {
                "name": "User Profiles",
                "url": "/admin/users/profile/",
                "icon": "fas fa-user-circle",
                "permissions": ["users.view_profile"]
            },
        ]
    },

    "custom_app_titles": {
        "django_celery_beat": "News Sync",
    },

    "custom_model_names": {
        "django_celery_beat.periodictask": "Scheduled Tasks",
        "django_celery_beat.intervalschedule": "Repeat Intervals",
        "django_celery_beat.crontabschedule": "Cron Schedules",
        "django_celery_beat.solarschedule": "Solar Schedules",
    },

    "search_model": [
        "news.Article",
        "users.Comment",
        "users.Profile",
    ],

    "topmenu_links": [
        {"name": "Home", "url": "/", "new_window": True},
        {"model": "news.article"},
        {"model": "community.comment"},
        {"app": "users"},
    ],

    "usermenu_links": [
        {"name": "Frontend", "url": "/", "new_window": True},
        {"name": "GitHub", "url": "https://github.com/your-bulleo-repo", "new_window": True},
    ],

    "icons": {
        "users.Profile": "fas fa-user-circle",
        "users.Comment": "fas fa-comment",
        "users.Notification": "fas fa-bell",
        "news.Article": "fas fa-newspaper",
        "news.NewsSource": "fas fa-globe",
        "news.Category": "fas fa-tags",
        "auth.User": "fas fa-users-cog",
    },

    "custom_app_icons": {
        "django_celery_beat": "fas fa-sync-alt",
    },

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [
        "auth",
    ],
    "hide_models": [
        "account.EmailAddress",
        "auth.Group",
        "users.Profile",
        "django_celery_beat.ClockedSchedule",
        "django_celery_beat.crontabschedule",
        "django_celery_beat.solarschedule",
    ],

}

JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",  # Options include: flatly, darkly, solar, cyborg, etc.
    "dark_mode_theme": "darkly",
    "navbar_small_text": True,
    "footer_fixed": True,
    "body_small_text": False,
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "collapsible",
    },
}

SITE_ID = config("SITE_ID", default=2, cast=int)

# Allauth Configurations for social logins
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_LOGIN_METHODS = {'username', 'email'}

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_LOGIN_REDIRECT_URL = "/"

SOCIALACCOUNT_ADAPTER = "apps.users.adapters.CustomSocialAccountAdapter"

ACCOUNT_SIGNUP_REDIRECT_URL = '/users/onboarding/'
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {
            "access_type": "online",
            "prompt": "select_account"  # Ensures account selection every time
        },
        "OAUTH_PKCE_ENABLED": True,  # For better security
    }
}

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "bulleo_session"

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://bulleo-4e729939848e.herokuapp.com",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Use Allauth's default URLs
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

# Admin Panel Logout Redirect
LOGOUT_REDIRECT_URL = "/accounts/logout/handler/"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "bulleo.news@gmail.com"
CONTACT_RECIPIENT_EMAIL = "bulleo.news@gmail.com"

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://bulleo-4e729939848e.herokuapp.com",
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
    "secure": True,
}

# Set Cloudinary as default file storage
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Media URL for Cloudinary
MEDIA_URL = f"https://res.cloudinary.com/{config('CLOUDINARY_CLOUD_NAME')}/"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# API Keys
GNEWS_API_KEY = config("GNEWS_API_KEY")

# Redis Configuration
REDIS_URL = config("REDIS_URL")

# Celery Configuration
CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")
CELERY_TIMEZONE = "UTC"

# Periodic Task Configuration
CELERY_BEAT_SCHEDULE = {
    'fetch-news-every-12-hours': {
        'task': 'apps.news.tasks.fetch_news_articles',
        'schedule': 43200.0,  # every 12 hours
    },
    'delete-old-articles-daily': {
        'task': 'apps.news.tasks.delete_expired_articles',
        'schedule': crontab(hour=0, minute=0),  # every day at midnight
    },
    'redis-heartbeat-every-5-days': {
        'task': 'apps.news.tasks.redis_heartbeat',
        'schedule': 5 * 86400.0,  # every 5 days
    },
}

# Set to True to skip fetching news articles if they are already cached
# Set to false to allow fetching even if cached
SKIP_FETCH_IF_CACHED = True

# Celery pytest configuration
if "pytest" in sys.modules:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

INTERNAL_IPS = [
    '127.0.0.1',
]

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
