from django.conf.urls import patterns, url
from exchange.storyscapes.annotations.urls import urlpatterns as _urlpatterns


urlpatterns = patterns(
    '',
    # maploom
    url(r'^story/new', 'geonode.maps.views.new_map',
        {'template': 'maps/story.html'}, name='maploom-story-new'),
    url(r'^story/(?P<storyid>[^/]+)/save$', 'maploom.geonode.views.save_story',
        name='save_story'),
    url(r'^maps/new/story', 'maploom.geonode.views.new_story_json',
        name='maploom-map-new3'),
    url(r'^maps/new$', 'geonode.maps.views.new_map',
        {'template': 'composer/maploom.html'}, name='maploom-map-new'),
    url(r'^maps/edit$', 'geonode.maps.views.new_map',
        {'template': 'composer/maploom.html'}, name='map-edit'),
    url(r'^maps/(?P<mapid>\d+)/view$', 'geonode.maps.views.map_view',
        {'template': 'composer/maploom.html'}, name='map-view'),
    url(r'^story/(?P<storyid>[^/]+)/draft$', 'mapstory.views.draft_view',
        {'template': 'composer/maploom.html'}, name='maploom-map-view'),
    url(r'^frame/(?P<storyid>[^/]+)/draft', 'mapstory.views.draft_view',
        name='draft_view'),
    # StoryTools
    url(r'^maps/(?P<mapid>\d+)/viewer$', 'geonode.maps.views.map_view',
        {'template': 'viewer/story_viewer.html'}, name='map-viewer'),
    url(r'^maps/(?P<mapid>\d+)/embed$', 'geonode.maps.views.map_view',
        {'template': 'viewer/story_viewer.html'}, name='map-viewer'),
    url(r'^story/(?P<mapid>\d+)/embed$', 'geonode.maps.views.mapstory_view',
        {'template': 'viewer/story_viewer.html'}, name='mapstory-viewer'),

)

urlpatterns += _urlpatterns
