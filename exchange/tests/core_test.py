import os
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from exchange.core.models import ThumbnailImage
from exchange.core.context_processors import resource_variables
from shutil import rmtree

test_img = os.path.join(os.path.dirname(__file__), 'test.png')
thumbs_dir = os.path.join(
    settings.MEDIA_ROOT,
    'thumbs'
)


class MockRequest:
    pass

request = MockRequest()


class ThumbnailImageModelTestCase(TestCase):

    def setUp(self):
        self.thumbnail_image = ThumbnailImage()
        self.site = AdminSite()
        self.ma = admin.ModelAdmin(ThumbnailImage, self.site)
        self.thumb = ThumbnailImage.objects.create(
            thumbnail_image=SimpleUploadedFile(
                name='test_thumb_delete_me.png',
                content=open(test_img, 'rb').read(),
                content_type='image/png',
            )
        )
        self.thumb.save()

    def test(self):
        self.assertEqual(
            self.ma.get_fieldsets(request),
            [(None,
                {'fields': ['thumbnail_image']})]
        )
        self.assertEqual(
            self.thumb.thumbnail_image.name,
            os.path.abspath(os.path.join(
                settings.MEDIA_ROOT,
                'thumbs',
                'test_thumb_delete_me.png'
            ))
        )
        self.assertEqual(
            self.thumb.thumbnail_image.height,
            150
        )
        self.assertEqual(
            self.thumb.thumbnail_image.width,
            250
        )

    def tearDown(self):
        rmtree(thumbs_dir)


class resource_variablesTestCase(TestCase):

    def setUp(self):
        self.defaults = resource_variables(request)

    def test(self):
        self.assertIn(
            'VERSION',
            self.defaults
        )
        self.assertIn(
            'REGISTRYURL',
            self.defaults
        )
        self.assertIn(
            'REGISTRY',
            self.defaults
        )
        self.assertIn(
            'MAP_CRS',
            self.defaults
        )
        self.assertIn(
            'INSTALLED_APPS',
            self.defaults
        )
        self.assertIn(
            'GEOAXIS_ENABLED',
            self.defaults
        )
