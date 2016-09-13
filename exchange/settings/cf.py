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

# TODO:
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

    print('auth_user = %s' % (AUTH_USER_MODEL))
