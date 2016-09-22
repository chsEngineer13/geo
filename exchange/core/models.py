# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.db import models
from solo.models import SingletonModel
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from resizeimage import resizeimage
from django import forms
import os


class ThumbnailImage(SingletonModel):
    thumbnail_image = models.ImageField(
        upload_to=os.path.join(settings.MEDIA_ROOT, 'thumbs'),
    )

    def save(self, *args, **kwargs):
        pil_image_obj = Image.open(self.thumbnail_image)
        new_image = resizeimage.resize_cover(
            pil_image_obj,
            [250, 150],
            validate=False
        )

        new_image_io = BytesIO()
        new_image.save(new_image_io, format='PNG')

        temp_name = self.thumbnail_image.name
        self.thumbnail_image.delete(save=False)

        self.thumbnail_image.save(
            temp_name,
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )

        super(ThumbnailImage, self).save(*args, **kwargs)


class ThumbnailImageForm(forms.Form):
    thumbnail_image = forms.FileField(
        label='Select a file',
    )
