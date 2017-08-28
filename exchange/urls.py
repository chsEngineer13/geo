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

from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
from maploom.geonode.urls import urlpatterns as maploom_urls
from fileservice.urls import urlpatterns as fileservice_urls
from thumbnails.urls import urlpatterns as thumbnail_urls
from geonode.urls import urlpatterns as geonode_urls
from . import views
from django.views.defaults import page_not_found
from storyscapes.urls import urlpatterns as story_urls
from django.contrib.auth.decorators import permission_required

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

    url(r'^csw$', permission_required('core.change_cswrecord', raise_exception=True)(views.CSWRecordList.as_view()), name='csw-record-list'),
    url(r'^csw/(?P<pk>[a-f0-9\-_]+)$', permission_required('core.change_cswrecord', raise_exception=True)(views.CSWRecordUpdate.as_view()), name='csw-record-update'),
    url(r'^csw/([a-f0-9\-_]+)/delete$', permission_required('core.delete_cswrecord', raise_exception=True)(views.delete_csw_view), name='csw-record-delete'),
    url(r'^csw/new/$', permission_required('core.add_cswrecord', raise_exception=True)(views.CSWRecordCreate.as_view()), name='csw-record-add'),
    url(r'^csw/search/$', permission_required('core.add_cswrecord', raise_exception=True)(views.csw_arcgis_search), name='csw_arcgis_search'),

    url(r'^about/', views.about_page, name='about')
)

if settings.REGISTRY is False:
    urlpatterns += [
        url(r'^services(.*)$', page_not_found)
    ]

if settings.ENABLE_SOCIAL_LOGIN is True:
    urlpatterns += [
        url('', include('social_django.urls', namespace='social'))
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

if settings.STORYSCAPES_ENABLED:
    urlpatterns += story_urls

if 'nearsight' in settings.INSTALLED_APPS:
    from nearsight.urls import urlpatterns as nearsight_urls
    urlpatterns += nearsight_urls

# use combined registry/geonode elastic search rather than geonode search
if settings.ES_UNIFIED_SEARCH:
    urlpatterns += [url(r'^api/(?P<resourcetype>base)/search/$',
                        views.unified_elastic_search,
                        name='unified_elastic_search')]
    urlpatterns += [url(r'^api/(?P<resourcetype>documents)/search/$',
                        views.unified_elastic_search,
                        name='unified_elastic_search')]
    urlpatterns += [url(r'^api/(?P<resourcetype>layers)/search/$',
                        views.unified_elastic_search,
                        name='unified_elastic_search')]
    urlpatterns += [url(r'^api/(?P<resourcetype>maps)/search/$',
                        views.unified_elastic_search,
                        name='unified_elastic_search')]
    urlpatterns += [url(r'^api/(?P<resourcetype>registry)/search/$',
                        views.unified_elastic_search,
                        name='unified_elastic_search')]
    urlpatterns += [url(r'^autocomplete', 
                        views.empty_page, 
                        name='autocomplete_override')]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += geonode_urls
urlpatterns += maploom_urls
urlpatterns += fileservice_urls
urlpatterns += thumbnail_urls
