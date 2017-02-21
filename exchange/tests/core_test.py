import os
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from exchange.core.models import ThumbnailImage, ThumbnailImageForm, CSWRecord
from shutil import rmtree

test_img = os.path.join(os.path.dirname(__file__), 'test.png')

class MockRequest:
    pass

request = MockRequest()


class ThumbnailImageModelTestCase(TestCase):
    def test(self):
        ti = ThumbnailImage(thumbnail_image = test_img)
        self.assertEqual(
            ti.height,
            150
        )
        self.assertEqual(
            ti.width,
            250
        )


class ThumbnailImageFormTestCase(TestCase):
    def setUp(self):
        self.thumbnail_image = ThumbnailImage(thumbnail_image = test_img)

    def test_init(self):
        ThumbnailImageForm(thumbnail_image = self.thumbnail_image)

    def test_init_without_image(self):
        with self.assertRaises(KeyError):
            ThumbnailImageForm()