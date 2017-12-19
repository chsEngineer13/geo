from django.db import models

from exchange.storyscapes.utils import parse_date_time

from datetime import datetime


class SpatioTemporalMixin(models.Model):

    the_geom = models.TextField(blank=True, null=True)

    start_time = models.BigIntegerField(blank=True, null=True)
    end_time = models.BigIntegerField(blank=True, null=True)

    @staticmethod
    def _timefmt(val):
        return datetime.isoformat(datetime.utcfromtimestamp(val))

    def set_start(self, val):
        self.start_time = parse_date_time(val)

    def set_end(self, val):
        self.end_time = parse_date_time(val)

    @property
    def start_time_str(self):
        return self._timefmt(self.start_time) if self.start_time else ''

    @property
    def end_time_str(self):
        return self._timefmt(self.end_time) if self.end_time else ''

    class Meta:
        abstract = True
