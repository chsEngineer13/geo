#
# API for handling Thumbnails in Exchange.
#

from django.db import models


class Thumbnail(models.Model):

    object_type = models.CharField(max_length=255, blank=False)
    object_id = models.CharField(max_length=255, blank=False)

    thumbnail_mime = models.CharField(max_length=127, null=True, blank=True)
    thumbnail_img = models.BinaryField(null=True, blank=True)

    class Meta:
        unique_together = ('object_type', 'object_id')
