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
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
from maploom.geonode.urls import urlpatterns as maploom_urls
from geonode.urls import urlpatterns as geonode_urls
from . import views
from django.views.defaults import page_not_found

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
    url(r'^developer/$', views.documentation_page, name='developer'),
    url(r'^csw/new/$', views.insert_csw, name='insert_csw'),
    url(r'^csw/status/$', views.csw_status, name='csw_status'),
    url(r'^csw/status_table/$', views.csw_status_table, name='csw_status_table'),
)

if settings.REGISTRY is False:
    urlpatterns += [
        url(r'^services(.*)$', page_not_found)
    ]

# If django-osgeo-importer is enabled...
if 'osgeo_importer' in settings.INSTALLED_APPS:
    # Replace the default Exchange 'layers/upload'
    from osgeo_importer.views import FileAddView
    urlpatterns += [
        url(
            r'^layers/upload$',
            login_required(FileAddView.as_view()),
            name='layer_upload'
        )
    ]
    # Add django-osgeo-importer URLs
    from osgeo_importer.urls import urlpatterns as osgeo_importer_urls
    urlpatterns += osgeo_importer_urls

# use combined registry/geonode elastic search rather than geonode search
if settings.ES_UNIFIED_SEARCH:
    urlpatterns += [url(r'^api/base/search/$', views.unified_elastic_search, name='unified_elastic_search')]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += geonode_urls
urlpatterns += maploom_urls
