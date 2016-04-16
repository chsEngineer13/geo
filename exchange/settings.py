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

# Set to True to load non-minified versions of (static) client dependencies
DEBUG_STATIC = False
TIME_ZONE = 'America/Chicago'
WSGI_APPLICATION = "exchange.wsgi.application"
ROOT_URLCONF = 'exchange.urls'
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

# static file settings
STATICFILES_DIRS.append(
    os.path.join(LOCAL_ROOT, "static"),
)
#STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(LOCAL_ROOT, 'static_root')
STATIC_URL = '/static/'

# media file storage
#MEDIA_ROOT = os.path.join(LOCAL_ROOT, 'uploaded')
MEDIA_URL = "/uploaded/"

# template settings
TEMPLATE_DIRS = (
    os.path.join(LOCAL_ROOT, "templates"),
) + TEMPLATE_DIRS

# installed applications
INSTALLED_APPS = (
    'geonode.contrib.geogig',
    'geonode.contrib.slack',
    'django_classification_banner',
    'maploom'
) + INSTALLED_APPS

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
        'LOCATION': 'http://localhost:8080/geoserver/',
        'PUBLIC_LOCATION': 'http://localhost:8080/geoserver/',
        'USER': 'admin',
        'PASSWORD': 'geoserver',
        'MAPFISH_PRINT_ENABLED': True,
        'PRINT_NG_ENABLED': True,
        'GEONODE_SECURITY_ENABLED': True,
        'GEOGIG_ENABLED': True,
        'WMST_ENABLED': False,
        'BACKEND_WRITE_ENABLED': True,
        'WPS_ENABLED': True,
        'GEOSERVER_DATA_DIR': '/var/lib/geoserver_data',
        'GEOGIG_DATASTORE_DIR': '/var/lib/geoserver_data/geogig',
        # Set to name of database in DATABASES dictionary to enable
        'DATASTORE': '',  # 'datastore',
        'TIMEOUT': 10  # number of seconds to allow for HTTP requests
    }
}

GEOGIG_DATASTORE_NAME = 'geogig-repo'

UPLOADER = {
    'BACKEND': 'geonode.rest',
    'OPTIONS': {
        'TIME_ENABLED': False,
        'GEOGIT_ENABLED': True,
    }
}


MAP_BASELAYERS = [
    {
        "source": {
            "ptype": "gxp_wmscsource",
            "url": OGC_SERVER['default']['LOCATION'] + "wms",
            "restUrl": "/gs/rest",
            "name": "local geoserver"
        }
    },
    {
        "source": {"ptype": "gxp_osmsource", "name": "OpenStreetMap"},
        "type": "OpenLayers.Layer.OSM",
        "name": "mapnik",
        "title": "OpenStreetMap",
        "args": ["OpenStreetMap"],
        "visibility": True,
        "fixed": True,
        "group":"background"
    }
]

TEMPLATE_CONTEXT_PROCESSORS += (
    'django_classification_banner.context_processors.classification',
    'exchange.core.context_processors.version',
)

if LOCKDOWN_GEONODE:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
        'geonode.security.middleware.LoginRequiredMiddleware',
    )

if CORS_ENABLED:
    INSTALLED_APPS = ('corsheaders',) + INSTALLED_APPS
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
        'corsheaders.middleware.CorsMiddleware',
    )
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_METHODS = ('GET',)

SECRET_KEY = 'x-#u&4x2k*$0-60fywnm5&^+&a!pd-ajrx(z@twth%i7^+oskh'

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

try:
    from local_settings import *  # noqa
except ImportError:
    pass

VAGRANT = os.environ.get('VAGRANT_ENABLED')
if VAGRANT:
    try:
        from dev.settings import *
    except ImportError:
        pass

CF_ENABLED = os.environ.get('CF_ENABLED')
if CF_ENABLED:
    try:
        from cf.settings import *
    except ImportError:
        pass
