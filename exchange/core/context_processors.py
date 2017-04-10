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

from django.conf import settings
from exchange.version import get_version


def resource_variables(request):
    """Global exchange values to pass to templates"""
    defaults = dict(
        VERSION=get_version(),
        REGISTRYURL=getattr(settings, 'REGISTRYURL', None),
        REGISTRY=getattr(settings, 'REGISTRY', False),
        MAP_CRS=getattr(settings, 'DEFAULT_MAP_CRS', None),
        ENABLE_SOCIAL_LOGIN=getattr(settings, 'ENABLE_SOCIAL_LOGIN', False),
        ENABLE_GOOGLE_LOGIN=getattr(settings, 'ENABLE_GOOGLE_LOGIN', False),
        ENABLE_FACEBOOK_LOGIN=getattr(settings, 'ENABLE_FACEBOOK_LOGIN', False),
        ENABLE_GEOAXIS_LOGIN=getattr(settings, 'ENABLE_GEOAXIS_LOGIN', False),
        INSTALLED_APPS=set(settings.INSTALLED_APPS),
        GEOAXIS_ENABLED=getattr(settings, 'GEOAXIS_ENABLED', False),
        MAP_PREVIEW_LAYER=getattr(settings, 'MAP_PREVIEW_LAYER', "''"),
        LOCKDOWN_EXCHANGE=getattr(settings, 'LOCKDOWN_GEONODE', False),
        LOGIN_WARNING=getattr(settings, 'LOGIN_WARNING_ENABLED', False),
        LOGIN_WARNING_TEXT=getattr(settings, 'LOGIN_WARNING_TEXT', "''"),
        STORYSCAPES_ENABLED=getattr(settings, 'STORYSCAPES_ENABLED', False)
    )

    return defaults
