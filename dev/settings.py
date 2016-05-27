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

SITEURL = 'http://192.168.99.110:8000/'

CLASSIFICATION_BANNER_ENABLED = True

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'exchange'
DATABASE_USER = 'exchange'
DATABASE_PASSWORD = 'boundless'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'

STATIC_ROOT = '/vagrant/dev/.django/static_root'
MEDIA_ROOT = '/vagrant/dev/.django/media'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    },
    'exchange_imports': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'exchange_data',
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    }
}

GEOSERVER_URL = 'http://192.168.99.110:8888/proxy/http://192.168.99.110:8080/geoserver/'
DEFAULT_MAP_CRS = "EPSG:4326"

OGC_SERVER = {
    'default': {
        'BACKEND': 'geonode.geoserver',
        'LOCATION': GEOSERVER_URL,
        'PUBLIC_LOCATION': GEOSERVER_URL,
        'USER': 'admin',
        'PASSWORD': 'geoserver',
        'MAPFISH_PRINT_ENABLED': True,
        'PRINT_NG_ENABLED': True,
        'GEONODE_SECURITY_ENABLED': True,
        'GEOGIG_ENABLED': True,
        'WMST_ENABLED': False,
        'BACKEND_WRITE_ENABLED': True,
        'WPS_ENABLED': True,
        'GEOSERVER_DATA_DIR': '/vagrant/dev/.geoserver/data',
        'GEOGIG_DATASTORE_DIR': '/vagrant/dev/.geoserver/data/geogig',
        'DATASTORE': 'exchange_imports',
        'TIMEOUT': 10
    }
}

GEOSERVER_BASE_URL = OGC_SERVER['default']['LOCATION'] + "wms"

MAP_BASELAYERS = [
    {
        "source": {
            "ptype": "gxp_wmscsource",
            "url": GEOSERVER_BASE_URL,
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

UPLOADER = {
    'BACKEND': 'geonode.rest',
    'OPTIONS': {
        'TIME_ENABLED': True,
        'GEOGIG_ENABLED': True,
    }
}

GEOGIG_DATASTORE_NAME = 'default-repo'
