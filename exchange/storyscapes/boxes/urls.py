# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'exchange.storyscapes.boxes.views',
    url(r'^$', 'boxes', name='boxes'),
)
