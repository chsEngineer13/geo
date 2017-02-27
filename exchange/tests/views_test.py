import os
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings
import pytest

django.setup()

test_img = os.path.join(os.path.dirname(__file__), 'test.png')
testdir = os.path.dirname(os.path.realpath(__file__))
User = get_user_model()

# bury these warnings for testing


class RemovedInDjango19Warning(Exception):
    pass


class ViewTestCase(TestCase):

    def common_setup(self):
        self.client = Client()
        admin_users = User.objects.filter(
            is_superuser=True
        )
        if admin_users.count() > 0:
            self.admin_user = admin_users[0]
        else:
            self.admin_user = User.objects.create_superuser(
                username='admin',
                email=''
            )
        self.admin_user.set_password('admin')
        self.admin_user.save()
        logged_in = self.client.login(
            username='admin',
            password='admin'
        )
        self.assertTrue(logged_in)

        self.expected_status = 200

    def get_response(self):
        self.response = self.client.get(self.url)
        self.assertIsNotNone(self.response)

    def status(self):
        self.assertEqual(
            self.response.status_code,
            self.expected_status
        )

    def doit(self):
        self.get_response()
        self.status()

    def postfile(self, file, name):
        with open(file, 'r') as f:
            response = self.client.post(self.url, {name: f})
        self.assertIsNotNone(response)
        self.assertEqual(
            response.status_code,
            302
        )


class HomeScreenTest(ViewTestCase):

    def setUp(self):
        self.common_setup()
        self.url = '/'

    def test(self):
        self.doit()


class LayerMetadataDetailTest(ViewTestCase):

    def setUp(self):
        from geonode.layers.utils import file_upload
        self.common_setup()
        self.layer = file_upload(
            os.path.join(testdir, 'test_point.shp'),
            name='testlayer'
        )
        self.url = '/layers/geonode:testlayer/metadata_detail'

    def test(self):
        self.doit()

    def test_thumb(self):
        self.postfile(test_img, 'thumbnail_image')


class MapMetadataDetailTest(ViewTestCase):
    def setUp(self):
        from geonode.maps.models import Map
        self.common_setup()
        self.map = Map.objects.create(
            owner=self.admin_user,
            zoom=0,
            center_x=0,
            center_y=0
        )
        self.url = '/maps/%s/metadata_detail' % self.map.id

    def test(self):
        self.doit()

    def test_thumb(self):
        self.postfile(test_img, 'thumbnail_image')


class GeoServerReverseProxyTest(ViewTestCase):

    def setUp(self):
        self.common_setup()
        self.url = '/wfsproxy/'

    def test(self):
        self.doit()


class HelpDocumentationPageTest(ViewTestCase):

    def setUp(self):
        self.common_setup()
        self.expected_status = 302
        self.url = '/help/'

    def test(self):
        self.doit()


class DeveloperDocumentationPageTest(ViewTestCase):

    def setUp(self):
        self.common_setup()
        self.expected_status = 302
        self.url = '/developer/'

    def test(self):
        self.doit()


class InsertCSWTest(ViewTestCase):

    def setUp(self):
        self.common_setup()
        self.url = '/csw/new/'

    def test(self):
        self.doit()

    @pytest.mark.skip
    def test_post(self):
        response = self.client.post(
            self.url,
            {
                'title': 'foo',
                'creator': 'me',
                'modified': '2017-01-01',
                'source': 'http://google.com'
            }
        )
        self.assertEqual(
            response.status_code,
            302
        )


class CSWStatusTest(ViewTestCase):

    def setUp(self):
        self.url = '/csw/status/'
        self.common_setup()

    def test(self):
        self.doit()

    def test_json(self):
        self.url = '/csw/status/?format=json'
        self.doit()


class CSWStatusTableTest(ViewTestCase):

    def setUp(self):
        self.common_setup()
        self.url = '/csw/status_table/'

    def test(self):
        self.doit()

@pytest.mark.skipif(settings.ES_UNIFIED_SEARCH==False,
                    reason="Only run if using unified search")
class UnifiedSearchTest(ViewTestCase):

    def setUp(self):
        self.common_setup()
        self.url = '/api/base/search/?limit=100&offset=0&q=test'
        self.expected_status = 200

    def test(self):
        self.doit()

    def test_phrase(self):
        self.url = '/api/base/search/?' \
                   'limit=100&offset=0&q="my phrase"'
        self.doit()

    def test_bool(self):
        self.url = '/api/base/search/?' \
                   'limit=100&offset=0&q=this and that'
        self.doit()

    def test_or(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=this or that'
        self.doit()

    def test_bbox(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&extent=0,0,0,0'
        self.doit()

    def test_date(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&' \
                   'date__gte=2000-01-01&date__lte=2000-01-02'
        self.doit()

    def test_categories(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&category__in=foo'
        self.doit()

    def test_keywords(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&keywords__in=foo'
        self.doit()

    def test_type(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&type__in=layer'
        self.doit()

    def test_datesorta(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&order_by=date'
        self.doit()

    def test_datesortd(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&order_by=-date'
        self.doit()

    def test_titlesorta(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&order_by=title'
        self.doit()

    def test_titlesortd(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&order_by=-title'
        self.doit()

    def test_countsortd(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test&' \
                   'order_by=-popular_count'
        self.doit()
