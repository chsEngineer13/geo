#
# API for handling Thumbnails in Exchange.
#

from django.db import models
from django.db.models.signals import post_save

from geonode.layers.models import Layer
from geonode.maps.models import Map

from . import get_gs_thumbnail


class Thumbnail(models.Model):

    object_type = models.CharField(max_length=255, blank=False)
    object_id = models.CharField(max_length=255, blank=False)

    thumbnail_mime = models.CharField(max_length=127, null=True, blank=True)
    thumbnail_img = models.BinaryField(null=True, blank=True)

    class Meta:
        unique_together = ('object_type', 'object_id')


# Check to see if an object already has a thumbnail.
def has_thumbnail(objectType, objectId):
    try:
        Thumbnail.objects.get(object_type=objectType, object_id=objectId)
        return True
    except Thumbnail.DoesNotExist:
        return False


# This is used as a post-save signal that will
# automatically geneirate a new thumbnail if none existed
# before it.
def generate_thumbnail(instance, sender, **kwargs):
    object_id = None
    obj_type = None
    if(instance.class_name == 'Map'):
        object_id = instance.id
        obj_type = 'maps'
    elif(instance.class_name == 'Layer'):
        object_id = instance.typename
        obj_type = 'layers'

    if(object_id is not None and not has_thumbnail(obj_type, object_id)):
        # have geoserver generate a preview png and return it.
        thumb_png = get_gs_thumbnail(instance)

        if(thumb_png is not None):
            # create a new thumbnail.
            thumb = Thumbnail(object_type=obj_type, object_id=object_id,
                              thumbnail_mime='image/png',
                              thumbnail_img=thumb_png)
            thumb.save()


# add this APIs signals for saving things.
post_save.connect(generate_thumbnail, sender=Layer)
post_save.connect(generate_thumbnail, sender=Map)
