"""
Django settings for ShopNeubs project.
Generated by 'django-admin startproject' using Django 1.10.5.
For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#v=%ja&h4m06$yx&o7dukkeyl_nvlt%2sh%ek5*d2kk3=h444f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    #'rest_auth.registration',

    'easy_thumbnails',
    'filer',
    'mptt',
    'django_hosts',
    'registration',
    'crispy_forms',
    'base',
    'division_territorial',
    'tercero',
    'inventario',
    'compras',
    'ventas',

]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

ROOT_URLCONF = 'ShopNeubs.urls'
ROOT_HOSTCONF = 'ShopNeubs.hosts'
DEFAULT_HOST = 'www'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'ShopNeubs.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ShopNeubs',
        'USER': 'postgres',
        'PASSWORD': '123456789',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
SESSION_CACHE_TIEMOUT = 60 * 60 * 24 * 3
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/shopneubs_cache',
        'TIMEOUT': SESSION_CACHE_TIEMOUT,
    }
}
# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Numero de dias de registrado los saldos inventarios
# Para marcarlos como nuevos
DAYS_PRODUCT_NEW = 15
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
LOGIN_URL = '/accounts/login/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

SESSION_COOKIE_AGE = 60 * 60 * 24 * 3
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_SAVE_EVERY_REQUEST = True
# Directorios para produccion
#STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR),"static_root","static")
MEDIA_ROOT = os.path.join(BASE_DIR,"media")

# Crispy Forms Settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Django REGISTRATION REDUX Settings
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.
REGISTRATION_AUTO_LOGIN = True # Automatically log the user in.

EMAIL_HOST = 'smtp.mi.com.co'
DEFAULT_FROM_EMAIL = 'shop@neubs.com.co'
#SERVER_EMAIL = 'ventas@neubs.com.co'
EMAIL_HOST_USER = 'shop@neubs.com.co'
EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxxxxx'
EMAIL_PORT = 465
#EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 60

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SITE_ID = 1

# Cantidad minima en los SELECT TOP (SELECT_TOP_MIN)
SELECT_TOP_MIN = 5
# Cantidad maxima en los SELECT TOP (SELECT_TOP_MAX)
SELECT_TOP_MAX = 10
# Cantidad maxima en los SELECT TOP para los elementos del index
SELECT_TOP_MAX_INDEX_ITEM = 8
# Número de productos a listar
NUM_ITEMS_DISPLAY = 10

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_ALIASES = {
   '': {
        #'large': {'size': (400, 300)},
        #'medium': {'size': (300, 300)},
        #'small': {'size': (100, 100)},
        # galeria del producto detalle
        'galeria': {'size': (70, 70),'crop':True,'upscale':True },
        # Imagen de los productos relacionados
        'producto_relacionado': {'size': (100, 100),'crop':True,'upscale':True },
        # Imagenes de los productos en el filtro producto
        'producto': {'size': (200, 200),'crop':True,'upscale':True, },
        # Imagen principal del producto detalle
        'producto_detalle': {'size': (350, 350),'crop':False,'upscale':True },
        # Carousel
        'carousel': {'size': (1800, 500),'crop':True,'upscale':True },
    },
}

#FILER_CANONICAL_URL = 'sharing/'
FILER_STORAGES = {
    'public': {
        'main': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(BASE_DIR, 'media/'),
                'base_url': '/media/',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': 'filer_public',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(BASE_DIR, 'media/'),
                'base_url': '/media/',
            },
        },
    },
}