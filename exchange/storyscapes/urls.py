from django.conf.urls import patterns, url
from exchange.storyscapes.annotations.urls import urlpatterns as _urlpatterns
from .views import save_story, new_story_json, new_chapter_json

urlpatterns = patterns(
    '',
    # maploom
    url(r'^story/chapter/new$', new_chapter_json, name='new_chapter'),
    url(r'^story/new$', 'geonode.maps.views.new_map',
        {'template': 'composer/editor.html'}, name='new_story'),
    url(r'^story$', new_story_json,
        name='new_story_json'),
    url(r'^story/(?P<storyid>[^/]+)/save$', save_story,
        name='save_story')

)

urlpatterns += _urlpatterns
