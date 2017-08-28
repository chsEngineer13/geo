import os
import pytest
from . import ExchangeTest
from exchange import settings


TESTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')

# bury these warnings for testing
class RemovedInDjango19Warning(Exception):
    pass


class ViewTestCase(ExchangeTest):

    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.login()

        self.url = '/'
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

    def test(self):
        self.doit()


class LayerMetadataDetailTest(ViewTestCase):

    def setUp(self):
        super(LayerMetadataDetailTest, self).setUp()

        from geonode.layers.utils import file_upload
        self.layer = file_upload(
            os.path.join(TESTDIR, 'test_point.shp'),
            name='testlayer'
        )
        self.url = '/layers/geonode:testlayer/metadata_detail'

    def test(self):
        self.doit()

class MapMetadataDetailTest(ViewTestCase):
    def setUp(self):
        super(MapMetadataDetailTest, self).setUp()

        from geonode.maps.models import Map
        self.map = Map.objects.create(
            owner=self.admin_user,
            zoom=0,
            center_x=0,
            center_y=0
        )
        self.url = '/maps/%s/metadata_detail' % self.map.id

    def test(self):
        self.doit()


class GeoServerReverseProxyTest(ViewTestCase):

    def setUp(self):
        super(GeoServerReverseProxyTest, self).setUp()
        self.url = '/wfsproxy/'

    def test(self):
        self.doit()


class HelpDocumentationPageTest(ViewTestCase):

    def setUp(self):
        super(HelpDocumentationPageTest, self).setUp()
        self.expected_status = 302
        self.url = '/help/'

    def test(self):
        self.doit()


class DeveloperDocumentationPageTest(ViewTestCase):

    def setUp(self):
        super(DeveloperDocumentationPageTest, self).setUp()
        self.expected_status = 302
        self.url = '/developer/'

    def test(self):
        self.doit()


class InsertCSWTest(ViewTestCase):

    def setUp(self):
        super(InsertCSWTest, self).setUp()
        self.url = '/csw/new/'

    def test(self):
        self.doit()

class CSWStatusTest(ViewTestCase):

    def setUp(self):
        super(CSWStatusTest, self).setUp()
        self.url = '/csw/status/'

    def test(self):
        self.doit()

    def test_json(self):
        self.url = '/csw/status/?format=json'
        self.doit()


class CSWStatusTableTest(ViewTestCase):

    def setUp(self):
        super(CSWStatusTableTest, self).setUp()
        self.url = '/csw/status_table/'

    def test(self):
        self.doit()


@pytest.mark.skipif(settings.ES_UNIFIED_SEARCH is False,
                    reason="Only run if using unified search")
class UnifiedSearchTest(ViewTestCase):

    def setUp(self):
        super(UnifiedSearchTest, self).setUp()
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

    def test_search_types(self):
        url = '/api/%s/search/?q=test'
        self.url = url % 'layers' 
        self.doit()

        self.url = url % 'documents' 
        self.doit()

        self.url = url % 'maps' 
        self.doit()

    def test_search_layer_by_id(self):
        self.url = '/api/layers/search/?id=1'
        self.doit()


# This doesn't test a view but performs a functional
# test on one of the views transformational objects.
#
@pytest.mark.skipif(settings.REGISTRYURL is None, reason="Only run if using registry")
class ViewFunctionTests(ViewTestCase):

    def test_get_unified_search_result_objects(self):
        from exchange.views import get_unified_search_result_objects

        test_hits = [{
            '_index': 'registry',
            '_source': {
                'bbox': [1,2,3,4],
            }
        }, {
            '_index': 'exchange',
            '_source': {
                'links' : {
                    'xml' : 'layers/exchange:dummy.xml',
                    'png' : 'layers/exchange:dummy/thumby.png'
                }
            }
        }]

        test_objects = get_unified_search_result_objects(test_hits)

        # validate that the bbox parses correct in 
        # the first result.

        self.assertEqual(test_objects[0]['bbox_left'], 1, 
                         'BBOX Was not formatted correctly!')

        self.assertEqual(test_objects[0]['bbox_top'], 4, 
                         'BBOX Was not formatted correctly!')


        # ensure the thumbnail link is generated.

        self.assertEqual(test_objects[1]['thumbnail_url'],
                         '%s/layers/exchange:dummy/thumby.png' % settings.REGISTRYURL,
                         'Wrong thumbnail URL (%s)' % test_objects[1]['thumbnail_url'])
