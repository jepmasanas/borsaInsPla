import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar variables d'entorn ABANS de fer res més
load_dotenv(BASE_DIR / '.env')

# Ara podem utilitzar os.getenv() per llegir les variables
SECRET_KEY = os.getenv('SECRET_KEY', 'meter la contraseña en el env de ser posible')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Notificacions d'administrador
NOTIFY_ADMIN_NEW_STUDENTS = os.getenv('NOTIFY_ADMIN_NEW_STUDENTS', 'True') == 'True'

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',') if h.strip()]
#CSRF_TRUSTED_ORIGINS = ['http://borsainspla.raspberryip.com', 'https://borsainspla.raspberryip.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'borsainspla_db'),
        'USER': os.getenv('DB_USER', 'borsainspla_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', '1234'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
# ============================================
# VALIDADORES DE CONTRASEÑA SIMPLIFICADOS
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    # Longitud mínima de 6 caracteres
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    # Requiere mayúscula y símbolo
    {
        'NAME': 'core.validators.ComplexityPasswordValidator',
    },
    
    # ========== VALIDADORES COMENTADOS (complejidad reducida) ==========
    # # Validador de similitud con atributos del usuario
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # # Validador de contraseñas comunes de Django
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # # No permitir contraseñas completamente numèriques
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
    # {
    #     'NAME': 'core.validators.SequencePasswordValidator',
    #     'OPTIONS': {
    #         'max_sequence_length': 3,
    #     }
    # },
    # # No permitir más de 2 caracteres repetidos (aaa, 111)
    # {
    #     'NAME': 'core.validators.RepeatedCharacterValidator',
    #     'OPTIONS': {
    #         'max_repeated': 2,
    #     }
    # },
    # # Bloquea patrones comunes inseguros
    # {
    #     'NAME': 'core.validators.CommonPatternsValidator',
    # },
]

LANGUAGE_CODE = 'ca'  # Idioma por defecto

# Idiomas disponibles
LANGUAGES = [
    ('ca', _('Català')),
    ('es', _('Español')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'BorsaPla <noreply-borsa@elpla.app>')
