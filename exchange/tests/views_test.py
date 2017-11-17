import os
import pytest
from . import ExchangeTest
from exchange import settings
import json
from osgeo_importer.tasks import import_object


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


class UploaderMixin:
    # Upload a file and create a new layer.
    #
    # @params {dict} files Keys are the form names,
    #                   Values are the paths to the files.
    # @params {dict} uploaderParams Extra parameters to change
    #                               the behaviour of theupload.
    #
    # TODO : Permissions options.
    #
    # @return The info for the layer as a dict.
    def upload_files(self, filenames, configs=None):
        from geonode.layers.models import Layer
        from osgeo_importer.models import UploadLayer
        outfiles = []
        for filename in filenames:
            path = self.get_file_path(filename)
            with open(path) as stream:
                data = stream.read()
            upload = SimpleUploadedFile(filename, data)
            outfiles.append(upload)
        response = self.client.post(
            reverse('uploads-new-json'),
            {'file': outfiles,
             'json': json.dumps(configs)},
            follow=True)
        content = json.loads(response.content)
        logger.debug('UPLOAD RESPONSE -------- %s', content)
        self.assertEqual(response.status_code, 200)
        uls = UploadLayer.objects.all()
        logger.debug('There are ----------------- %s ---------------------- Upload Layers', uls.count())
        for testul in uls:
            logger.debug('UploadLayer %s %s %s', testul.id, testul.task_id, testul.import_status)
        # Configure Uploaded Files
        upload_id = content['id']
        upload_layers = UploadLayer.objects.filter(upload_id=upload_id)

        retval = []

        response = self.client.get('/importer-api/data-layers',
                                   content_type='application/json' )
        logger.debug('UPLOAD LAYERS %s', response.content)
        for testul in uls:
            logger.debug('UploadLayer %s %s %s', testul.id, testul.task_id, testul.import_status)

        for upload_layer in upload_layers:
            for cfg in configs:
                logger.debug('CFG: %s', cfg)
                config = cfg['config']
                config['upload_layer_id'] = upload_layer.id
                logger.debug('CONFIG: %s', config)
                import_object(upload_layer.upload_file.id, config)
                retval.append(upload_layer)
        return retval


class HomeScreenTest(ViewTestCase):

    def test(self):
        self.doit()

class AboutPageTest(ViewTestCase):

    def setUp(self):
        super(AboutPageTest, self).setUp()
        self.expected_status = 200
        self.url = '/about/'

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


class LayerPublishTest(ViewTestCase):

    def setUp(self):
        super(LayerPublishTest, self).setUp()

        from geonode.layers.utils import file_upload
        self.layer = file_upload(
            os.path.join(TESTDIR, 'test_point.shp'),
            name='testlayer'
        )
        self.url = '/layers/geonode:testlayer/publish'
        # We expect to be redirected
        self.expected_status = 302

    def test(self):
        self.layer.is_published = False
        self.layer.save()
        self.doit()
        from geonode.layers.models import Layer
        self.layer = Layer.objects.get(id=self.layer.id)
        self.assertEqual(self.layer.is_published, True)


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


@pytest.mark.skipif(settings.ES_UNIFIED_SEARCH is False,
                    reason="Only run if using unified search")
class UnifiedSearchTest(ViewTestCase, UploaderMixin):

    def setUp(self):
        super(UnifiedSearchTest, self).setUp()
        self.url = '/api/base/search/?limit=100&offset=0&q=test'
        self.expected_status = 200

        from geonode.layers.models import Layer
        from osgeo_importer.models import UploadLayer
        from geonode.maps.models import Map
        from geonode.base.models import TopicCategory, Region

        # Layer
        # TODO: Make sure this upload is working
        files = ['./relief_san_andres.tif', './boxes_with_end_date.zip']
        configs = [{'upload_file_name': 'test_point.zip'},
                   {'upload_file_name': 'boxes_with_end_date.zip'}]
        # Upload the layer
        upload_layers = self.upload_files(files, configs)
        test_layer = upload_layers[0]
        test_layer2 = upload_layers[1]
        # test_layers should hold test layer objects
        # abstracts
        test_layer.abstract = 'hello world'
        test_layer2.abstract = 'foo bar'
        # categories
        # air
        test_layer.category = TopicCategory.objects.all()[0]
        # basemaps
        test_layer2.category = TopicCategory.objects.all()[1]
        # regions
        # Africa
        test_layer.regions.add(Region.objects.all()[1])
        # keywords
        test_layer.keywords.add('foo')
        test_layer2.keywords.add('bar')
        # popular_count
        test_layer.popular_count = 10
        test_layer2.popular_count = 20
        # define an owner
        test_layer2.owner = self.admin_user
        # save
        test_layer.save()
        test_layer2.save()

        # Map
        # This creates an empty map (contains no layers)
        test_map = Map.objects.create(
            owner=self.admin_user,
            zoom=0,
            center_x=0,
            center_y=0
        )
        # test_map should hold a test map object
        # rename it
        test_map.title = 'MapTest'
        test_map.save()

        # TODO: Documents are not currently reflected correctly in search API
        # Document
        document = {
            'title': 'Test Document',
            # Does this need to be placed in a list?
            'file': 'test.png'
            # url and link to fields are not required
        }
        doc_form = DocumentCreateForm(document)
        self.assertTrue(doc_form.is_valid(), "Test document failed validation")
        test_doc = doc_form.save()
        test_doc.save()
        # test_doc should hold a test document object

        # CSW Registry
        record = {
            'title': 'Test CSW Layer',
            'modified': '01/01/2001',
            'creator': 'Automated Testing',
            'record_type': 'layer',
            'alternative': 'test',
            'abstract': 'This was created from automated testing.',
            'source': 'http://foo.org/a.html',
            'relation': '',
            'record_format': 'csw',
            'bbox_upper_corner': '45,45',
            'bbox_lower_corner': '0,0',
            'contact_email': 'test@boundlessgeo.fake',
            'contact_phone': '555-555-5555',
            'gold': '',
            'category': ''
        }

        form = CSWRecordForm(record)
        self.assertTrue(form.is_valid(), "Test record failed validation")

        test_record = form.save()
        test_record.save()
        create_new_csw.apply(args=(new_record.id,)).get()
        # test_record should hold a test csw record
        # Should be valid & available in registry
        self.test_layer = test_layer
        self.test_layer2 = test_layer2
        self.test_map = test_map

    # After self.doit(), self.response.content will hold the JSON response
    # from performing GET on self.url
    def test(self):
        self.doit()

    def test_phrase(self):
        # should be test_layer
        self.url = '/api/base/search/?' \
                   'limit=100&offset=0&q="test"'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer.id)

    def test_bool(self):
        # this functions on abstract
        # should be test_layer2
        self.url = '/api/base/search/?' \
                   'limit=100&offset=0&q=foo and bar'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)

    def test_or(self):
        # should get test_layer and test_layer2
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&q=test or boxes'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(len(search_results['objects']), 2)

    def test_bbox(self):
        # This will grab test_layer
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&extent=-120,-120,25,50'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        # should be test_layer's id
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer.id)

    def test_date(self):
        # these should get nothing
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&' \
                   'date__gte=2000-01-01&date__lte=2000-01-02'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 0)
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&' \
                   'date__gte=2000-01-01&date__gte=9999-01-02'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 0)
        # these should get everything
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&' \
                   'date__gte=2000-01-01&date__lte=9999-01-02'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 3)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 3)
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&' \
                   'date__gte=2000-01-01&date__gte=0999-01-02'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 3)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 3)

    def test_categories(self):
        # Should get test_layer2, assigned to air category
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&category__in=air'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        # should be test_layer2's id
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)

    def test_keywords(self):
        # Should get test_layer, given foo keyword
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&keywords__in=foo'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        # should be test_layer's id
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer.id)

    def test_type(self):
        # should get both layers
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&type=layer'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(len(search_results['objects']), 2)
        # should get map
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&type=map'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 1)

    def test_datesorta(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&order_by=date'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 3)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 3)
        # Should get first uploaded first, so test_layer first
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer.id)
        # test_layer2 should be second
        self.assertEqual(search_results['objects'][1]['id'], self.test_layer2.id)
        # test_map should be last
        self.assertEqual(search_results['objects'][2]['id'], self.test_map.id)

    def test_datesortd(self):
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&order_by=-date'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 3)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 3)
        # Should get "most recent" first, so test_map first
        self.assertEqual(search_results['objects'][0]['id'], self.test_map.id)
        # test_layer2 should be second
        self.assertEqual(search_results['objects'][1]['id'], self.test_layer2.id)
        # test_layer2 should be last
        self.assertEqual(search_results['objects'][2]['id'], self.test_layer.id)

    def test_titlesorta(self):
        # alphabetical order
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&order_by=title'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 3)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 3)
        # test_layer2 comes alphabetically first
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)
        # test_map comes second
        self.assertEqual(search_results['objects'][1]['id'], self.test_map.id)
        # test_layer comes last
        self.assertEqual(search_results['objects'][2]['id'], self.test_layer.id)

    def test_titlesortd(self):
        # reverse alphabetical order
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&order_by=-title'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 3)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 3)
        # test_layer comes alphabetically last
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer.id)
        # test_map comes second
        self.assertEqual(search_results['objects'][1]['id'], self.test_map.id)
        # test_layer2 comes first
        self.assertEqual(search_results['objects'][2]['id'], self.test_layer2.id)

    def test_countsortd(self):
        # highest popular_count value comes first
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&' \
                   'order_by=-popular_count'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 3)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 2)
        self.assertEqual(search_results['meta']['facets']['type']['map'], 1)
        self.assertEqual(len(search_results['objects']), 3)
        # test_layer2 is most popular
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)
        self.assertEqual(search_results['objects'][1]['id'], self.test_layer.id)
        # test_map is least popular
        self.assertEqual(search_results['objects'][2]['id'], self.test_map.id)

    def test_owner(self):
        # should get test_layer2
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&owner__username=admin'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(len(search_results['objects']), 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)

    def test_regions(self):
        # should get test_layer
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&regions=Africa'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(len(search_results['objects']), 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer.id)

    def test_time(self):
        # failure case - no layers returned
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&extent__lte=2000-01-02'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 0)
        # success case - test_layer2 returned
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&extent__lte=2003-01-02'
        self.doit()
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(len(search_results['objects']), 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)
        # failure case - no layers returned
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&extent__gte=2003-01-02'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 0)
        # success case - test_layer2 returned
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&extent__gte=2000-01-02'
        self.doit()
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(len(search_results['objects']), 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)
        # failure case - no layers returned
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&extent__range=2002-03-02,2004-03-02'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 0)
        # success case - test_layer2 returned
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&extent__range=2000-01-02,2001-03-01'
        self.doit()
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(len(search_results['objects']), 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)

    def test_subtype(self):
        # gets test_layer2
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&subtype=vector'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(len(search_results['objects']), 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer2.id)
        # gets test_layer
        self.url = '/api/base/search/' \
                   '?limit=100&offset=0&subtype=raster'
        self.doit()
        search_results = json.loads(self.response.content)
        self.assertEqual(search_results['meta']['total_count'], 1)
        self.assertEqual(search_results['meta']['facets']['type']['layer'], 1)
        self.assertEqual(len(search_results['objects']), 1)
        self.assertEqual(search_results['objects'][0]['id'], self.test_layer.id)

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
