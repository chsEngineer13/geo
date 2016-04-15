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
from exchange.settings import *

LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, '.geonode/static_root')
AUTH_LDAP = os.environ.get('AUTH_LDAP')

if AUTH_LDAP > 0:
    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
        'guardian.backends.ObjectPermissionBackend',
    )

    AUTH_LDAP_SERVER_URI = os.environ.get('AUTH_LDAP_SERVER_URI')

    import ldap
    from django_auth_ldap.config import LDAPSearch

    LDAP_SEARCH_DN = os.environ.get('LDAP_SEARCH_DN')
    AUTH_LDAP_USER = os.environ.get('AUTH_LDAP_USER')
    AUTH_LDAP_USER_DN_TEMPLATE = os.environ.get('AUTH_LDAP_USER_DN_TEMPLATE')
    AUTH_LDAP_BIND_DN = os.environ.get('AUTH_LDAP_BIND_DN')
    AUTH_LDAP_BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD')
    AUTH_LDAP_USER_ATTR_MAP = {
        'first_name': 'givenName',
        'last_name': 'sn',
        'email': 'mail',
    }
    AUTH_LDAP_USER_SEARCH = LDAPSearch(LDAP_SEARCH_DN,
                                       ldap.SCOPE_SUBTREE, AUTH_LDAP_USER)
CF_DEBUG = os.environ.get('CF_DEBUG')

if CF_DEBUG > 0:
    DEBUG = True

if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ.get('SECRET_KEY')

AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
AWS_S3_DOMAIN = S3_CUSTOM_DOMAIN if S3_CUSTOM_DOMAIN else 's3.amazonaws.com'
AWS_S3_BUCKET_DOMAIN = '%s.%s' % (AWS_STORAGE_BUCKET_NAME, AWS_S3_DOMAIN)
MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_BUCKET_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'cf.s3utils.MediaStorage'

POSTGIS = os.environ.get('POSTGIS_URL')
DATABASES = {
    'default': dj_database_url.config(conn_max_age=500),
    'datastore': dj_database_url.parse(POSTGIS, conn_max_age=500)
}

GS_URL = os.environ.get('GS_URL')
OGC_SERVER = {
    'default': {
        'BACKEND': 'geonode.geoserver',
        'LOCATION': GS_URL,
        'PUBLIC_LOCATION': GS_URL,
        'USER': os.environ.get('GS_USER'),
        'PASSWORD': os.environ.get('GS_PASSWORD'),
        'MAPFISH_PRINT_ENABLED': True,
        'PRINT_NG_ENABLED': True,
        'GEONODE_SECURITY_ENABLED': True,
        'GEOGIG_ENABLED': True,
        'WMST_ENABLED': False,
        'DATASTORE': 'datastore',
        'GEOGIG_DATASTORE_DIR': '/var/lib/geoserver_data/geogig',
    }
}

GEOGIG_DATASTORE_NAME = 'geogig-repo'
UPLOADER = {
    'BACKEND': 'geonode.importer',
    'OPTIONS': {
        'TIME_ENABLED': True,
        'GEOGIG_ENABLED': True,
    }
}

ES_ENGINE = 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': ES_ENGINE,
        'URL': os.environ.get('ES_URL'),
        'INDEX_NAME': os.environ.get('ES_INDEX', 'exchange'),
    },
}

BROKER_URL = os.environ.get('RABBITMQ_URL')
CELERY_ALWAYS_EAGER = False
NOTIFICATION_QUEUE_ALL = not CELERY_ALWAYS_EAGER

INSTALLED_APPS += (
    'storages',
    'haystack',
)
