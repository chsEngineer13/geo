from django.db import models
from solo.models import SingletonModel
from colorfield.fields import ColorField

class SiteName(SingletonModel):
    site_name = models.CharField(max_length=75, default='Exchange')

    def __unicode__(self):
        return u"Site Name"

    class Meta:
        verbose_name = "Site Name"

class TagLine(SingletonModel):
    tag_line = models.CharField(max_length=75, default='A Platform for Geospatial Collaboration', help_text="A Platform for Geospatial Collaboration")

    def __unicode__(self):
        return u"Tag Line"

    class Meta:
        verbose_name = "Tag Line"

class BannerImage(SingletonModel):
    banner_image = models.ImageField(upload_to='static/img/', help_text="Recommended dimensions: 1440px x 350px")

    def __unicode__(self):
        return u"Banner Image"

    class Meta:
        verbose_name = "Banner Image"

class IconImage(SingletonModel):
    icon_image = models.ImageField(upload_to='static/img/', help_text="Recommended dimensions: 96px x 96px")

    def __unicode__(self):
        return u"Icon Image"

    class Meta:
        verbose_name = "Icon Image"

class LogoImage(SingletonModel):
    logo_image = models.ImageField(upload_to='static/img/', help_text="Must be 35px wide")

    def __unicode__(self):
        return u"Logo Image"

    class Meta:
        verbose_name = "Logo Image"

class NavbarColor(SingletonModel):
    color = ColorField(default='#0F1A2C')

    def __unicode__(self):
        return u"Navigation Bar Color"

    class Meta:
        verbose_name = "Navigation Bar Color"
