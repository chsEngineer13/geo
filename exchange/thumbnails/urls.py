
from django.conf.urls import url

from .views import thumbnail_view

urlpatterns = (
    url(r'^thumbnails/(?P<objectType>maps|documents|layers)/(?P<objectId>.+)$',
        thumbnail_view, name='thumbnail_handler'),
)
