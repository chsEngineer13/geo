# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'exchange.storyscapes.annotations.views',
    url(r'^maps/(?P<mapid>\d+)/annotations$',
        'annotations',
        name='annotations')
)
