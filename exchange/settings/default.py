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
import geonode
from geonode.settings import *

SITENAME = 'exchange'
CLASSIFICATION_BANNER_ENABLED = False
DEBUG = TEMPLATE_DEBUG = True
CORS_ENABLED = True
LOCKDOWN_GEONODE = True
REGISTRATION_OPEN = False
SOCIAL_BUTTONS = False
SECRET_KEY = 'exchange@q(6+mnr&=jb@z#)e_cix10b497vzaav61=de5@m3ewcj9%ctc'

# Set to True to load non-minified versions of (static) client dependencies
DEBUG_STATIC = False
TIME_ZONE = 'America/Chicago'
WSGI_APPLICATION = "exchange.wsgi.application"
ROOT_URLCONF = 'exchange.urls'
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

# static file settings
# need to fix all the missing files in geonode
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
APP_ROOT = os.path.join(os.path.join(LOCAL_ROOT, os.pardir))
PROJECT_ROOT = os.path.join(os.path.join(APP_ROOT, os.pardir))
STATICFILES_DIRS.append(
    os.path.join(APP_ROOT, "static"),
)
STATIC_ROOT = os.path.join(PROJECT_ROOT, '.storage/static_root')
STATIC_URL = '/static/'

# media file storage
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '.storage/media')
MEDIA_URL = "/uploaded/"

# template settings
TEMPLATE_DIRS = (
    os.path.join(APP_ROOT, "templates"),
) + TEMPLATE_DIRS

TEMPLATE_CONTEXT_PROCESSORS += (
    'django_classification_banner.context_processors.classification',
    'exchange.core.context_processors.version',
)

# middlware
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

# installed applications
INSTALLED_APPS = (
    'exchange.core',
    'geonode.contrib.geogig',
    'geonode.contrib.slack',
    'django_classification_banner',
    'maploom',
    'solo',
    'colorfield',
    'haystack',
    'corsheaders'
) + INSTALLED_APPS

# cors settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ('GET',)

# database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(LOCAL_ROOT, 'development.db'),
    }
}

# geoserver settings
OGC_SERVER = {
    'default': {
        'BACKEND': 'geonode.geoserver',
        'LOCATION': 'http://127.0.0.1:8080/geoserver/',
        'PUBLIC_LOCATION': 'http://127.0.0.1:8080/geoserver/',
        'USER': 'admin',
        'PASSWORD': 'geoserver',
        'MAPFISH_PRINT_ENABLED': True,
        'PRINT_NG_ENABLED': True,
        'GEONODE_SECURITY_ENABLED': True,
        'GEOGIG_ENABLED': True,
        'WMST_ENABLED': False,
        'BACKEND_WRITE_ENABLED': True,
        'WPS_ENABLED': True,
        'LOG_FILE': '/var/lib/geoserver_data/logs/geoserver.log',
        'GEOSERVER_DATA_DIR': '/var/lib/geoserver_data',
        'GEOGIG_DATASTORE_DIR': '/var/lib/geoserver_data/geogig',
        'DATASTORE': '',
        'TIMEOUT': 10
    }
}

GEOGIG_DATASTORE_NAME = 'geogig-repo'

UPLOADER = {
    'BACKEND': 'geonode.importer',
    'OPTIONS': {
        'TIME_ENABLED': True,
        'GEOGIT_ENABLED': True,
    }
}

DOWNLOAD_FORMATS_VECTOR = [
    'JPEG', 'PDF', 'PNG', 'Zipped Shapefile', 'GML 2.0', 'GML 3.1.1', 'CSV',
    'Excel', 'GeoJSON', 'KML', 'View in Google Earth',
]
DOWNLOAD_FORMATS_RASTER = [
    'JPEG',
    'PDF',
    'PNG',
    'ArcGrid',
    'GeoTIFF',
    'Gtopo30',
    'ImageMosaic',
    'KML',
    'View in Google Earth',
    'GML',
    'GZIP'
]

# haystack settings
ES_ENGINE = 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': ES_ENGINE,
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'exchange',
    },
}

# amqp settings
BROKER_URL = 'amqp://guest@127.0.0.1:5672'
CELERY_ALWAYS_EAGER = False
NOTIFICATION_QUEUE_ALL = not CELERY_ALWAYS_EAGER
NOTIFICATION_LOCK_LOCATION = LOCAL_ROOT

# openlayers settings
#MAP_BASELAYERS = [
#    {
#        "source": {
#            "ptype": "gxp_wmscsource",
#            "url": OGC_SERVER['default']['LOCATION'] + "wms",
#            "restUrl": "/gs/rest",
#            "name": "local geoserver"
#        }
#    },
#    {
#        "source": {"ptype": "gxp_osmsource", "name": "OpenStreetMap"},
#        "type": "OpenLayers.Layer.OSM",
#        "name": "mapnik",
#        "title": "OpenStreetMap",
#        "args": ["OpenStreetMap"],
#        "visibility": True,
#        "fixed": True,
#        "group":"background"
#    }
#]

try:
    from local_settings import *  # noqa
except ImportError:
    pass
