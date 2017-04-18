from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields

from geonode.maps.models import Map

from .mixins import SpatioTemporalMixin

import logging

logger = logging.getLogger(__name__)


class FrameManager(models.Manager):

    def copy_frames(self, source_id, target):
        source = self.objects.get(id=source_id)
        copies = []

        logger.debug('copy from', source_id, source.Frame_set.all())
        logger.debug('to target', target.id)

        for frame in source.Frame_set.all():
            frame.map = target
            frame.pk = None
            copies.append(frame)

        logger.debug(copies)

        Frame.objects.bulk_create(copies)


class Frame(SpatioTemporalMixin):

    # The Frame or frame of interest (FOI) represents the
    # geographic extent of an event. It can be used to provide
    # a spatial context for the narrative or to restrict the
    # aspect ratio to a specific geographic area or point for
    # a determined time range. You can also configure a playback
    # rate and interval rate for the frame runtime playback.

    objects = FrameManager()

    PLAYBACK_RATE = (('seconds', 'Seconds'), ('minutes', 'Minutes'),)
    INTERVAL_RATE = (('minutes', 'Minutes'), ('hours', 'Hours'),
                     ('weeks', 'Weeks'), ('months', 'Months'),
                     ('years', 'Years'),)

    #content_type = models.ForeignKey(ContentType)
    #object_id = models.PositiveIntegerField()
    #content_object = fields.GenericForeignKey('content_type', 'object_id')

    map = models.ForeignKey(Map)

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    data = models.TextField(blank=True, null=True)
    center = models.TextField(blank=True, null=True)

    interval = models.IntegerField(blank=True, null=True)
    intervalRate = models.CharField(max_length=10, choices=INTERVAL_RATE,
                                    blank=True, null=True)

    playback = models.IntegerField(blank=True, null=True)
    playbackRate = models.CharField(max_length=10, choices=PLAYBACK_RATE,
                                    blank=True, null=True)

    speed = models.TextField(blank=True, null=True)
    zoom = models.IntegerField(blank=True, null=True)
    layers = models.TextField(blank=True, null=True)
    resolution = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Frame"