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

from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from maploom.geonode.urls import urlpatterns as maploom_urls
from hypermap.urls import urlpatterns as hypermap_urls
from geonode.urls import urlpatterns as geonode_urls
from . import views

js_info_dict = {
    'packages': ('geonode.layers',),
}

urlpatterns = patterns(
    '',
    url(r'^/?$', views.home_screen, name='home'),
    url(r'^layers/(?P<layername>[^/]*)/metadata_detail$',
        views.layer_metadata_detail, name='layer_metadata_detail'),
    url(r'^maps/(?P<mapid>[^/]*)/metadata_detail$', views.map_metadata_detail,
        name='map_metadata_detail'),
    url(r'^wfsproxy/', views.geoserver_reverse_proxy,
        name='geoserver_reverse_proxy'),
    # Redirect help and developer links to the documentation page
    url(r'^help/$', views.documentation_page, name='help'),
    url(r'^developer/$', views.documentation_page, name='developer')
)

urlpatterns += geonode_urls
urlpatterns += maploom_urls
urlpatterns += hypermap_urls
