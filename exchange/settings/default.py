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
import hypermap
import dj_database_url
from geonode.settings import *
from datetime import timedelta

SITEURL = SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')
ALLOWED_HOSTS = [SITE_URL, ]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITENAME = 'exchange'
CLASSIFICATION_BANNER_ENABLED = False
DEBUG = TEMPLATE_DEBUG = True
CORS_ENABLED = True

LOCKDOWN_GEONODE = os.getenv('LOCKDOWN_GEONODE', True)
if LOCKDOWN_GEONODE is not None:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
        'geonode.security.middleware.LoginRequiredMiddleware',
    )

REGISTRATION_OPEN = False
SOCIAL_BUTTONS = False
SECRET_KEY = 'exchange@q(6+mnr&=jb@z#)e_cix10b497vzaav61=de5@m3ewcj9%ctc'

# Set to True to load non-minified versions of (static) client dependencies
DEBUG_STATIC = False
TIME_ZONE = 'America/Chicago'
WSGI_APPLICATION = "exchange.wsgi.application"
ROOT_URLCONF = 'exchange.urls'

LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.join(os.path.join(LOCAL_ROOT, os.pardir))
PROJECT_ROOT = os.path.join(os.path.join(APP_ROOT, os.pardir))

# static files storage
STATICFILES_DIRS.append(os.path.join(APP_ROOT, "static"),)
# not sure why django.contrib.staticfiles is not auto collecting static files
STATIC_ROOT = os.path.join(PROJECT_ROOT, '.storage/static_root')
STATIC_URL = '/static/'

# media file storage
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '.storage/media')
MEDIA_URL = '/media/'

# template settings
TEMPLATE_DIRS = (
    os.path.join(APP_ROOT, "templates"),
) + TEMPLATE_DIRS

TEMPLATE_CONTEXT_PROCESSORS += (
    'django_classification_banner.context_processors.classification',
    'exchange.core.context_processors.resource_variables',
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


# geoserver settings
GEOSERVER_URL = os.environ.get('GEOSERVER_URL',
                               'http://127.0.0.1:8080/geoserver/')
GEOSERVER_USER = os.environ.get('GEOSERVER_USER',
                                'admin')
GEOSERVER_PASSWORD = os.environ.get('GEOSERVER_PASSWORD',
                                    'geoserver')
GEOSERVER_LOG = os.environ.get('GEOSERVER_LOG',
                               '/var/lib/geoserver_data/logs/geoserver.log')
GEOSERVER_DATA_DIR = os.environ.get('GEOSERVER_DATA_DIR',
                                    '/var/lib/geoserver_data')
GEOGIG_DATASTORE_DIR = os.environ.get('GEOSERVER_DATA_DIR',
                                      '/var/lib/geoserver_data/geogig')
OGC_SERVER = {
    'default': {
        'BACKEND': 'geonode.geoserver',
        'LOCATION': GEOSERVER_URL,
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
        'DATASTORE': '',
        'TIMEOUT': 10
    }
}

GEOGIG_DATASTORE_NAME = 'geogig-repo'

MAP_BASELAYERS[0]['source']['url'] = OGC_SERVER['default']['LOCATION'] + 'wms'

# database settings
SQLITEDB = "sqlite:///%s" % os.path.join(LOCAL_ROOT,'development.db')
DATABASE_URL = os.getenv('DATABASE_URL', SQLITEDB)
DATABASES['default'] = dj_database_url.parse(DATABASE_URL,
                                             conn_max_age=600)
POSTGIS_URL = os.environ.get('POSTGIS_URL', None)
if POSTGIS_URL is not None:
    DATABASES['exchange_imports'] = dj_database_url.parse(POSTGIS_URL,
                                                          conn_max_age=600)
    OGC_SERVER['default']['DATASTORE'] = 'exchange_imports'

UPLOADER = {
    'BACKEND': 'geonode.importer',
    'OPTIONS': {
        'TIME_ENABLED': True,
        'GEOGIT_ENABLED': True,
    }
}

WGS84_MAP_CRS = os.environ.get('WGS84_MAP_CRS', None)
if WGS84_MAP_CRS is not None:
    DEFAULT_MAP_CRS = "EPSG:4326"

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
ES_URL = os.environ.get('ES_URL', 'http://127.0.0.1:9200/')
ES_ENGINE = 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': ES_ENGINE,
        'URL': ES_URL,
        'INDEX_NAME': 'exchange',
    },
}

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

CELERYBEAT_SCHEDULE = {
    'Check All Services': {
        'task': 'check_all_services',
        'schedule': timedelta(minutes=15)
    },
}
CELERY_TIMEZONE = 'UTC'

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

# registry
REGISTRY = os.environ.get('REGISTRY', None)
if REGISTRY is not None:
    from hypermap.settings import REGISTRY_PYCSW

    REGISTRY = True # ensure the value is True
    REGISTRYURL = '%s/registry' % SITE_URL.rstrip('/')
    CATALOGLIST = [
        {
            'name': 'local registry',
            'url': '%s/hypermap/' % SITE_URL.rstrip('/')
        },
    ]
    SEARCH_ENABLED = True
    SEARCH_TYPE = 'elasticsearch'
    SEARCH_URL = ES_URL
    INSTALLED_APPS = (
        'djmp',
        'hypermap.aggregator',
        'hypermap.dynasty',
        'hypermap.search',
        'hypermap',
    ) + INSTALLED_APPS
    MAPPROXY_CONFIG = os.path.join(MEDIA_ROOT, 'mapproxy_config')

    REGISTRY_PYCSW['server']['url'] = SITE_URL.rstrip('/') + '/registry/search/csw'

    REGISTRY_PYCSW['metadata:main'] = {
        'identification_title': 'Registry Catalogue',
        'identification_abstract': 'Registry, a Harvard Hypermap project, is an application that manages ' \
        'OWS, Esri REST, and other types of map service harvesting, and maintains uptime statistics for ' \
        'services and layers.',
        'identification_keywords': 'sdi,catalogue,discovery,metadata,registry,HHypermap',
        'identification_keywords_type': 'theme',
        'identification_fees': 'None',
        'identification_accessconstraints': 'None',
        'provider_name': 'Organization Name',
        'provider_url': SITE_URL,
        'contact_name': 'Lastname, Firstname',
        'contact_position': 'Position Title',
        'contact_address': 'Mailing Address',
        'contact_city': 'City',
        'contact_stateorprovince': 'Administrative Area',
        'contact_postalcode': 'Zip or Postal Code',
        'contact_country': 'Country',
        'contact_phone': '+xx-xxx-xxx-xxxx',
        'contact_fax': '+xx-xxx-xxx-xxxx',
        'contact_email': 'Email Address',
        'contact_url': 'Contact URL',
        'contact_hours': 'Hours of Service',
        'contact_instructions': 'During hours of service. Off on weekends.',
        'contact_role': 'Point of Contact'
    }
    TAGGIT_CASE_INSENSITIVE = True


try:
    from local_settings import *  # noqa
except ImportError:
    pass
