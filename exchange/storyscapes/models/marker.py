from django.db import models
from geonode.maps.models import Map

from .mixins import SpatioTemporalMixin

import logging

logger = logging.getLogger(__name__)


class MarkerManager(models.Manager):

    def copy_map_Markers(self, source_id, target):
        source = Map.objects.get(id=source_id)
        copies = []
        logger.debug('copy from', source_id, source.Marker_set.all())
        logger.debug('to target', target.id)
        for marker in source.Marker_set.all():
            marker.map = target
            marker.pk = None
            copies.append(marker)
        logger.debug(copies)
        Marker.objects.bulk_create(copies)


class Marker(SpatioTemporalMixin):
    objects = MarkerManager()

    map = models.ForeignKey(Map)
    title = models.TextField()
    content = models.TextField(blank=True, null=True)
    media = models.TextField(blank=True, null=True)

    in_timeline = models.BooleanField(default=False)
    in_map = models.BooleanField(default=False)
    appearance = models.TextField(blank=True, null=True)

    auto_show = models.BooleanField(default=False)
    pause_playback = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title
