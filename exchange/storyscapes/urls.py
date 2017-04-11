from django.conf.urls import patterns, url
from exchange.storyscapes.annotations.urls import urlpatterns as _urlpatterns
from .views import save_story

urlpatterns = patterns(
    '',
    # maploom
    url(r'^story/new', 'geonode.maps.views.new_map',
        {'template': 'composer/v1/story.html'}, name='new_story'),
    url(r'^story/(?P<storyid>[^/]+)/save$', save_story,
        name='save_story')

)

urlpatterns += _urlpatterns
