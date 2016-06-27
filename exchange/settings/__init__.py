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
from .default import *  # noqa
from datetime import timedelta

#####
BASE_URL = os.getenv('BASE_URL', 'localhost')
BASE_PORT = os.getenv('PORT', '8000')

SITE_URL = 'http://%s:%s' % (BASE_URL, BASE_PORT)

ALLOWED_HOSTS = [BASE_URL, ]

CELERYBEAT_SCHEDULE = {
    'Check All Services': {
        'task': 'aggregator.tasks.check_all_services',
        'schedule': timedelta(minutes=15)
    },
}

CLOUD_FOUNDRY = os.getenv('CLOUD_FOUNDRY', None)

#TODO:
# - Enable postgis settings.
# - Lockdown geonode.

if CLOUD_FOUNDRY is not None:
    vcap_service_config = os.environ.get('VCAP_SERVICES')
    decoded_config = json.loads(vcap_service_config)    

    vcap_app_config = os.environ.get('VCAP_APPLICATION')
    # Use postgres
    DATABASES = {'default': dj_database_url.config()}

    # use rabbit
    if 'cloudamqp' in decoded_config:
        BROKER_URL = decoded_config['cloudamqp'][0]['credentials']['uri']

    SEARCH_ENABLED = True
    SEARCH_TYPE = 'elasticsearch'
    SEARCH_URL = decoded_config['searchly'][0]['credentials']['sslUri']

    SKIP_CELERY_TASK = False

    print 'auth_user = %s' % (AUTH_USER_MODEL)

VARIABLES = []

LOCKDOWN_GEONODE = os.getenv('LOCKDOWN_GEONODE', None)
if LOCKDOWN_GEONODE is not None:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
        'geonode.security.middleware.LoginRequiredMiddleware',
    )
else:
    VARIABLES.append('$LOCKDOWN_GEONODE')

# Service Settings
WGS84_MAP_CRS = os.environ.get('WGS84_MAP_CRS', "EPSG:4326")

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
