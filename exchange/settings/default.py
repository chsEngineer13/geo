# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
import dj_database_url
import copy
from geonode.settings import *  # noqa
from geonode.settings import (
    MIDDLEWARE_CLASSES,
    STATICFILES_DIRS,
    INSTALLED_APPS,
    CELERY_IMPORTS,
    MAP_BASELAYERS,
    DATABASES,
    CATALOGUE
)


def str2bool(v):
    if v and len(v) > 0:
        return v.lower() in ("yes", "true", "t", "1")
    else:
        return False

SITENAME = os.getenv('SITENAME', 'exchange')
WSGI_APPLICATION = "exchange.wsgi.application"
ROOT_URLCONF = 'exchange.urls'
SOCIAL_BUTTONS = str2bool(os.getenv('SOCIAL_BUTTONS', 'False'))

USE_TZ = str2bool(os.getenv('USE_TZ', 'True'))

# classification banner
CLASSIFICATION_BANNER_ENABLED = str2bool(os.getenv(
    'CLASSIFICATION_BANNER_ENABLED',
    'False')
)
CLASSIFICATION_TEXT = os.getenv('CLASSIFICATION_TEXT', 'UNCLASSIFIED//FOUO')
CLASSIFICATION_TEXT_COLOR = os.getenv('CLASSIFICATION_TEXT_COLOR', 'white')
CLASSIFICATION_BACKGROUND_COLOR = os.getenv(
    'CLASSIFICATION_BACKGROUND_COLOR',
    'green'
)
CLASSIFICATION_LINK = os.getenv('CLASSIFICATION_LINK', None)

# registration
EMAIL_HOST = os.getenv('EMAIL_HOST', None)
EMAIL_PORT = os.getenv('EMAIL_PORT', None)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', None)
THEME_ACCOUNT_CONTACT_EMAIL = os.getenv('THEME_ACCOUNT_CONTACT_EMAIL', None)
ACCOUNT_ACTIVATION_DAYS = os.getenv('ACCOUNT_ACTIVATION_DAYS', 7)

# path setup
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.join(LOCAL_ROOT, os.pardir)

# static files storage
STATICFILES_DIRS.append(os.path.join(APP_ROOT, "static"),)

# template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(APP_ROOT, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.tz',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.account',
                'geonode.context_processors.resource_urls',
                'geonode.geoserver.context_processors.geoserver_urls',
                'django_classification_banner.context_processors.'
                'classification',
                'exchange.core.context_processors.resource_variables',
            ],
            'debug': DEBUG,
        },
    },
]

# middleware
MIDDLEWARE_CLASSES = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
) + MIDDLEWARE_CLASSES

ADDITIONAL_APPS = os.environ.get(
    'ADDITIONAL_APPS',
    ()
)

if isinstance(ADDITIONAL_APPS, str):
    ADDITIONAL_APPS = tuple(map(str.strip, ADDITIONAL_APPS.split(',')))

OSGEO_IMPORTER_ENABLED = str2bool(os.getenv('OSGEO_IMPORTER_ENABLED', 'False'))
GEONODE_CLIENT_ENABLED = str2bool(os.getenv('GEONODE_CLIENT_ENABLED', 'True'))

# installed applications
INSTALLED_APPS = (
    'flat',
    'exchange.core',
    'exchange.themes',
    'geonode',
    'geonode.contrib.geogig',
    'geonode.contrib.slack',
    'django_classification_banner',
    'maploom',
    'solo',
    'exchange-docs',
) + ADDITIONAL_APPS + INSTALLED_APPS

if OSGEO_IMPORTER_ENABLED:
    INSTALLED_APPS = ('osgeo_importer',) + INSTALLED_APPS
else:
    UPLOADER = {
        'BACKEND': 'geonode.importer',
        'OPTIONS': {
            'TIME_ENABLED': True,
            'MOSAIC_ENABLED': False,
        }
    }

if GEONODE_CLIENT_ENABLED:
    INSTALLED_APPS = ('geonode-client',) + INSTALLED_APPS
    LAYER_PREVIEW_LIBRARY = 'react'

# authorized exempt urls
ADDITIONAL_AUTH_EXEMPT_URLS = os.environ.get(
    'ADDITIONAL_AUTH_EXEMPT_URLS',
    ()
)

if isinstance(ADDITIONAL_AUTH_EXEMPT_URLS, str):
    ADDITIONAL_AUTH_EXEMPT_URLS = tuple(map(str.strip, ADDITIONAL_AUTH_EXEMPT_URLS.split(',')))

AUTH_EXEMPT_URLS = ('/api/o/*', '/api/roles', '/api/adminRole', '/api/users', '/o/token/*', '/o/authorize/*',) + ADDITIONAL_AUTH_EXEMPT_URLS

# geoserver settings
GEOSERVER_URL = os.environ.get(
    'GEOSERVER_URL',
    'http://127.0.0.1:8080/geoserver/'
)
GEOSERVER_LOCAL_URL = os.environ.get(
    'GEOSERVER__LOCAL_URL',
    GEOSERVER_URL
)
GEOSERVER_USER = os.environ.get(
    'GEOSERVER_USER',
    'admin'
)
GEOSERVER_PASSWORD = os.environ.get(
    'GEOSERVER_PASSWORD',
    'geoserver'
)
GEOSERVER_LOG = os.environ.get(
    'GEOSERVER_LOG',
    '/opt/geonode/geoserver_data/logs/geoserver.log'
)
GEOSERVER_DATA_DIR = os.environ.get(
    'GEOSERVER_DATA_DIR',
    '/opt/geonode/geoserver_data'
)
GEOGIG_DATASTORE_DIR = os.environ.get(
    'GEOSERVER_DATA_DIR',
    '/opt/geonode/geoserver_data/geogig'
)
PG_DATASTORE = os.getenv('PG_DATASTORE', 'exchange_imports')
PG_GEOGIG = str2bool(os.getenv('PG_GEOGIG', 'True'))

OGC_SERVER = {
    'default': {
        'BACKEND': 'geonode.geoserver',
        'LOCATION': GEOSERVER_LOCAL_URL,
        'LOGIN_ENDPOINT': 'j_spring_oauth2_geonode_login',
        'LOGOUT_ENDPOINT': 'j_spring_oauth2_geonode_logout',
        'PUBLIC_LOCATION': GEOSERVER_URL,
        'USER': GEOSERVER_USER,
        'PASSWORD': GEOSERVER_PASSWORD,
        'MAPFISH_PRINT_ENABLED': True,
        'PRINT_NG_ENABLED': True,
        'GEONODE_SECURITY_ENABLED': True,
        'GEOGIG_ENABLED': True,
        'WMST_ENABLED': False,
        'BACKEND_WRITE_ENABLED': True,
        'WPS_ENABLED': True,
        'LOG_FILE': GEOSERVER_LOG,
        'GEOSERVER_DATA_DIR': GEOSERVER_DATA_DIR,
        'GEOGIG_DATASTORE_DIR': GEOGIG_DATASTORE_DIR,
        'DATASTORE': PG_DATASTORE,
        'PG_GEOGIG': PG_GEOGIG,
        'TIMEOUT': 10,
        'LOGOUT_ENDPOINT': 'j_spring_oauth2_geonode_logout'
    }
}

GEOSERVER_BASE_URL = OGC_SERVER['default']['PUBLIC_LOCATION'] + 'wms'
GEOGIG_DATASTORE_NAME = 'geogig-repo'

MAP_BASELAYERS[0]['source']['url'] = (OGC_SERVER['default']
                                      ['PUBLIC_LOCATION'] + 'wms')

POSTGIS_URL = os.environ.get(
    'POSTGIS_URL',
    'postgis://exchange:boundless@localhost:5432/exchange_data'
)
DATABASES['exchange_imports'] = dj_database_url.parse(
    POSTGIS_URL,
    conn_max_age=600
)

WGS84_MAP_CRS = str2bool(os.environ.get('WGS84_MAP_CRS', False))
if WGS84_MAP_CRS:
    DEFAULT_MAP_CRS = "EPSG:4326"

# local pycsw
CATALOGUE['default']['URL'] = '%s/catalogue/csw' % SITEURL.rstrip('/')

'''
unified search settings
ES_UNIFIED_SEARCH must be set to True
Elastic Search for both Registry and GeoNode must running
on same elasticsearch instance at ES_URL
REGISTRY_URL must be set in order to provide links to Registry
'''
ES_UNIFIED_SEARCH = str2bool(os.environ.get('ES_UNIFIED_SEARCH', 'False'))

# haystack settings
ES_URL = os.environ.get('ES_URL', 'http://127.0.0.1:9200/')
ES_ENGINE = os.environ.get(
    'ES_ENGINE',
    'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
)
HAYSTACK_SEARCH = str2bool(os.getenv('HAYSTACK_SEARCH', 'False'))
if ES_UNIFIED_SEARCH == True:
    HAYSTACK_SEARCH = True
if HAYSTACK_SEARCH:
    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': ES_ENGINE,
            'URL': ES_URL,
            'INDEX_NAME': 'exchange',
        },
    }
    INSTALLED_APPS = (
        'haystack',
    ) + INSTALLED_APPS


# amqp settings
BROKER_URL = os.environ.get('BROKER_URL', 'amqp://guest:guest@localhost:5672/')
CELERY_ALWAYS_EAGER = False
NOTIFICATION_QUEUE_ALL = not CELERY_ALWAYS_EAGER
NOTIFICATION_LOCK_LOCATION = LOCAL_ROOT
SKIP_CELERY_TASK = False
CELERY_DEFAULT_EXCHANGE = 'exchange'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'rpc' + BROKER_URL[4:]
CELERYD_PREFETCH_MULTIPLIER = 25
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE
CELERY_IMPORTS += ('exchange.tasks',)

# Logging settings
# 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'
DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'ERROR')

installed_apps_conf = {
    'handlers': ['console'],
    'level': DJANGO_LOG_LEVEL,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
                ('%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d'
                 ' %(message)s'),
        },
    },
    'handlers': {
        'console': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        app: copy.deepcopy(installed_apps_conf) for app in INSTALLED_APPS
    },
    'root': {
        'handlers': ['console'],
        'level': DJANGO_LOG_LEVEL
    },
}

LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'propagate': False,
    'level': 'WARNING',  # Django SQL logging is too noisy at DEBUG
}

# Authentication Settings

# ldap
AUTH_LDAP_SERVER_URI = os.environ.get('AUTH_LDAP_SERVER_URI', None)
LDAP_SEARCH_DN = os.environ.get('LDAP_SEARCH_DN', None)
if all([AUTH_LDAP_SERVER_URI, LDAP_SEARCH_DN]):
    from ._ldap import *   # noqa

# geoaxis
GEOAXIS_ENABLED = str2bool(os.getenv('GEOAXIS_ENABLED', 'False'))
if GEOAXIS_ENABLED:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.RemoteUserBackend',
    ) + AUTHENTICATION_BACKENDS
    for i, middleware in enumerate(MIDDLEWARE_CLASSES):
        # Put custom middleware class after AuthenticationMiddleware
        if middleware == 'django.contrib.auth.middleware.AuthenticationMiddleware':
            MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
            MIDDLEWARE_CLASSES.insert(i+1, 'exchange.auth.middleware.GeoAxisMiddleware')


# NEED TO UPDATE DJANGO_MAPLOOM FOR ONLY THIS ONE VALUE
REGISTRY = os.environ.get('ENABLE_REGISTRY', False)
REGISTRYURL = os.environ.get('REGISTRYURL', None)
REGISTRY_CAT = os.environ.get('REGISTRY_CAT', 'registry')

# If django-osgeo-importer is enabled, give it the settings it needs...
if 'osgeo_importer' in INSTALLED_APPS:
    import pyproj
    # Point django-osgeo-importer, if enabled, to the Exchange database
    OSGEO_DATASTORE = 'exchange_imports'
    # Tell it to use the GeoNode compatible mode
    OSGEO_IMPORTER_GEONODE_ENABLED = True
    # Tell celery to load its tasks
    CELERY_IMPORTS += ('osgeo_importer.tasks',)
    # override GeoNode setting so importer UI can see when tasks finish
    CELERY_IGNORE_RESULT = False
    IMPORT_HANDLERS = [
        # If GeoServer handlers are enabled, you must have an instance of
        # geoserver running.
        # Warning: the order of the handlers here matters.
        'osgeo_importer.handlers.FieldConverterHandler',
        'osgeo_importer.handlers.geoserver.GeoserverPublishHandler',
        'osgeo_importer.handlers.geoserver.GeoserverPublishCoverageHandler',
        'osgeo_importer.handlers.geoserver.GeoServerTimeHandler',
        'osgeo_importer.handlers.geoserver.GeoWebCacheHandler',
        'osgeo_importer.handlers.geoserver.GeoServerBoundsHandler',
        'osgeo_importer.handlers.geoserver.GenericSLDHandler',
        'osgeo_importer.handlers.geonode.GeoNodePublishHandler',
        'osgeo_importer.handlers.geoserver.GeoServerStyleHandler',
        'osgeo_importer.handlers.geonode.GeoNodeMetadataHandler'
    ]
    PROJECTION_DIRECTORY = os.path.join(
        os.path.dirname(pyproj.__file__),
        'data/'
    )


try:
    from local_settings import *  # noqa
except ImportError:
    pass

# Use https:// scheme in Gravatar URLs
AVATAR_GRAVATAR_SSL = True

# TODO: disable pickle serialization when we can ensure JSON works everywhere
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
SESSION_COOKIE_AGE = 60 * 60 * 24

# Set default access to layers to all, user will need to deselect the checkbox
# manually
DEFAULT_ANONYMOUS_VIEW_PERMISSION = True
DEFAULT_ANONYMOUS_DOWNLOAD_PERMISSION = True
