from django.db import models
from solo.models import SingletonModel
from colorfield.fields import ColorField
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from resizeimage import resizeimage

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

    def save(self, *args, **kwargs):
        pil_image_obj = Image.open(self.banner_image)
        new_image = resizeimage.resize_cover(pil_image_obj, [1440, 350], validate=False)

        new_image_io = BytesIO()
        new_image.save(new_image_io, format='PNG')

        temp_name = self.banner_image.name
        self.banner_image.delete(save=False)

        self.banner_image.save(
            temp_name,
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )

        super(BannerImage, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"Banner Image"

    class Meta:
        verbose_name = "Banner Image"

class IconImage(SingletonModel):
    icon_image = models.ImageField(upload_to='static/img/', help_text="Recommended dimensions: 96px x 96px")

    def save(self, *args, **kwargs):
        pil_image_obj = Image.open(self.icon_image)
        new_image = resizeimage.resize_cover(pil_image_obj, [96, 96], validate=False)

        new_image_io = BytesIO()
        new_image.save(new_image_io, format='PNG')

        temp_name = self.icon_image.name
        self.icon_image.delete(save=False)

        self.icon_image.save(
            temp_name,
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )

        super(IconImage, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"Icon Image"

    class Meta:
        verbose_name = "Icon Image"

class LogoImage(SingletonModel):
    logo_image = models.ImageField(upload_to='static/img/', help_text="Must be 35px wide")

    def save(self, *args, **kwargs):
        pil_image_obj = Image.open(self.logo_image)
        new_image = resizeimage.resize_height(pil_image_obj, 35, validate=False)

        new_image_io = BytesIO()
        new_image.save(new_image_io, format='PNG')

        temp_name = self.logo_image.name
        self.logo_image.delete(save=False)

        self.logo_image.save(
            temp_name,
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )

        super(LogoImage, self).save(*args, **kwargs)

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
