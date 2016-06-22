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

import dj_database_url
import json
import os
from .default import *  # noqa

VARIABLES = []

SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')
ALLOWED_HOSTS = [SITE_URL, ]

LOCKDOWN_GEONODE = os.getenv('LOCKDOWN_GEONODE', None)
if LOCKDOWN_GEONODE is not None:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
        'geonode.security.middleware.LoginRequiredMiddleware',
    )
else:
    VARIABLES.append('$LOCKDOWN_GEONODE')

# Django Database Settings
DATABASE_URL = os.getenv('DATABASE_URL', None)
if DATABASE_URL is not None:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)
else:
    VARIABLES.append('$DATABASE_URL')

# PostGIS Database Settings
POSTGIS_URL = os.environ.get('POSTGIS_URL', None)
if POSTGIS_URL is not None:
    DATABASES['exchange_imports'] = dj_database_url.parse(POSTGIS_URL,
                                                          conn_max_age=600)
    OGC_SERVER['default']['DATASTORE'] = 'exchange_imports'
else:
    VARIABLES.append('$POSTGIS_URL')

# Service Settings
WGS84_MAP_CRS = os.environ.get('WGS84_MAP_CRS', None)
if WGS84_MAP_CRS is not None:
    DEFAULT_MAP_CRS = "EPSG:4326"
else:
    VARIABLES.append('$WGS84_MAP_CRS')

GEOSERVER_URL = os.environ.get('GEOSERVER_URL', None)
if GEOSERVER_URL is not None:
    OGC_SERVER['default']['LOCATION'] = GEOSERVER_URL
    OGC_SERVER['default']['PUBLIC_LOCATION'] = GEOSERVER_URL
    OGC_SERVER['default']['DATASTORE'] = 'exchange_imports'
    GEOSERVER_BASE_URL = GEOSERVER_URL + 'wms'
    MAP_BASELAYERS[0]['source']['url'] = GEOSERVER_BASE_URL
else:
    VARIABLES.append('$WGS84_MAP_CRS')

GEOSERVER_DATA_DIR = os.environ.get('GEOSERVER_DATA_DIR', None)
if GEOSERVER_DATA_DIR is not None:
    OGC_SERVER['default']['GEOSERVER_DATA_DIR'] = GEOSERVER_DATA_DIR

GEOGIG_DATASTORE_DIR = os.environ.get('GEOGIG_DATASTORE_DIR', None)
if GEOSERVER_URL is not None:
    OGC_SERVER['default']['GEOGIG_DATASTORE_DIR'] = GEOGIG_DATASTORE_DIR

GEOSERVER_LOG = os.environ.get('GEOSERVER_LOG', None)
if GEOSERVER_LOG is not None:
    OGC_SERVER['default']['LOG_FILE'] = GEOSERVER_LOG

ES_URL = os.environ.get('ES_URL', None)
if ES_URL is not None:
    HAYSTACK_CONNECTIONS['default']['URL'] = ES_URL
else:
    VARIABLES.append('$ES_URL')

AMQP_URL = os.environ.get('AMQP_URL', None)
if ES_URL is not None:
    BROKER_URL = AMQP_URL
else:
    VARIABLES.append('$AMQP_URL')

# Authentication Settings
AUTH_LDAP_SERVER_URI = os.environ.get('AUTH_LDAP_SERVER_URI', None)
LDAP_SEARCH_DN = os.environ.get('LDAP_SEARCH_DN', None)
if all([AUTH_LDAP_SERVER_URI, LDAP_SEARCH_DN]):

    import ldap
    from django_auth_ldap.config import LDAPSearch

    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
        'guardian.backends.ObjectPermissionBackend',
    )
    AUTH_LDAP_USER = os.environ.get('AUTH_LDAP_USER', '(uid=%(user)s)')
    AUTH_LDAP_BIND_DN = os.environ.get('AUTH_LDAP_BIND_DN', '')
    AUTH_LDAP_BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD', '')
    AUTH_LDAP_USER_ATTR_MAP = {
        'first_name': 'givenName', 'last_name': 'sn', 'email': 'mail',
    }
    AUTH_LDAP_USER_SEARCH = LDAPSearch(LDAP_SEARCH_DN,
                                       ldap.SCOPE_SUBTREE, AUTH_LDAP_USER)
if AUTH_LDAP_SERVER_URI is None:
    VARIABLES.append('$AUTH_LDAP_SERVER_URI')
if AUTH_LDAP_SERVER_URI is None:
    VARIABLES.append('$LDAP_SEARCH_DN')

print "The following variables were not found: \n%s" % VARIABLES
