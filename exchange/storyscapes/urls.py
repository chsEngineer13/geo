from django.conf.urls import patterns, url, include
from .views import save_story, new_story_json, new_chapter_json, draft_view

from tastypie.api import Api

from api import StoryResource

v1_api = Api(api_name='v1')

v1_api.register(StoryResource())

urlpatterns = patterns(
    '',
    # maploom
    url(r'^story/chapter/new$', new_chapter_json, name='new_chapter'),
    url(r'^story/new$', 'geonode.maps.views.new_map',
        {'template': 'composer/editor.html'}, name='new_story'),
    url(r'^story$', new_story_json,
        name='new_story_json'),
    url(r'^story/(?P<storyid>[^/]+)/save$', save_story,
        name='save_story'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^story/(?P<story_id>[^/]+)/draft$',
    draft_view, {'template': 'composer/editor.html'}, name='composer-draft-view'),

)
