from django.conf import settings
from geonode.api.resourcebase_api import CommonModelApi, CommonMetaApi
from .models import Story


class StoryResource(CommonModelApi):
    """Story API"""

    class Meta(CommonMetaApi):
        queryset = Story.objects.distinct().order_by('-date')
        if settings.RESOURCE_PUBLISHING:
            queryset = queryset.filter(is_published=True)
        resource_name = 'stories'