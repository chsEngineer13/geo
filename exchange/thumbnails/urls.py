
from django.conf.urls import patterns, url, include

from .views import thumbnail_view

urlpatterns = (
    url(r'^thumbnails/(?P<objectType>map|document|layer)/(?P<objectId>.+)$',
        thumbnail_view, name='thumbnail_handler'),
)
