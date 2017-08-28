# Perform tests for unified search
from . import ExchangeTest
from exchange.core.forms import CSWRecordForm
from exchange.tasks import create_new_csw
from geonode.documents.forms import DocumentCreateForm


@pytest.mark.skipif(settings.ES_UNIFIED_SEARCH is False,
                    reason="Only run if using unified search")
class SearchTest(ExchangeTest):
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
                                   content_type='application/json')
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

    def test(self):
        from geonode.layers.models import Layer
        from osgeo_importer.models import UploadLayer
        from geonode.maps.models import Map

        # Layer
        files = ['./test_point.zip']
        configs = [{'upload_file_name': 'test_point.zip'}]
        # Upload the layer
        upload_layers = self.upload_files(files, configs)
        test_layer = upload_layers[0]
        # test_layer should hold a test layer object

        # Map
        # This creates an empty map (contains no layers)
        test_map = Map.objects.create(
            owner=self.admin_user,
            zoom=0,
            center_x=0,
            center_y=0
        )
        # test_map should hold a test map object

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
        self.login()

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

        # testing all objects
        print 'layer: {}, map: {}'.format(test_layer, test_map)
        print 'doc: {}, csw: {}'.format(test_doc, test_record)
