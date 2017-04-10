from tastypie.api import Api

from api import StoryResource

api = Api(api_name='api')

api.register(StoryResource())
