# Perform tests against the uploader.
#
#

import os
import json
import re
import time
import datetime
import pytz

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from . import ExchangeTest
from osgeo_importer.tasks import import_object

import pytest

from exchange import settings
import logging
logger = logging.getLogger(__name__)

# This is a dummy exception class
#  used to make back tracing easier.
class UploaderException(Exception):
    pass

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

    def drop_layer(self, uri=None):
        working_uri = uri+'/remove'
        drop_r = self.client.post(working_uri, follow=False)
        self.assertEqual(drop_r.status_code, 302,
                         "Did not return expected forwaring code!")

class UploadLayerTest(UploaderMixin, ExchangeTest):
    
    def setUp(self):
        super(UploadLayerTest, self).setUp()
        self.login()

    # This is a meta function for executing uploader options.
    #
    # Uploads the shapefile, checks on the layer, and drops it.
    #
    #  def _test_meta(self, files, configs={}):
    #    layer_uri = self.upload_files(files, configs).get('url', None)
    #    if(layer_uri is not None):
    #        self.drop_layer(uri=layer_uri)

    def test_temporalextent_upload(self):
        from geonode.layers.models import Layer
        from osgeo_importer.models import UploadLayer
        files = ['./boxes_with_end_date.zip']
        configs = [
            {
                'upload_file_name': 'boxes_with_end_date.zip',
                'config': 
                    {
                        'index': 0,
                        'convert_to_date': ['date', 'enddate'],
                        'start_date': 'date',
                        'end_date': 'enddate',
                        'configureTime': True
                    }
            }

        ]
        upload_layers = self.upload_files(files, configs)
        logger.debug('Upload %s', upload_layers)
        layername = upload_layers[0].layer_name

        layer = Layer.objects.get(name=layername)
        self.assertEqual(layer.temporal_extent_start,
                         datetime.datetime(2000, 3, 1, 0, 0, tzinfo=pytz.utc))
        self.assertEqual(layer.temporal_extent_end,
                         datetime.datetime(2001, 3, 1, 0, 0, tzinfo=pytz.utc))

        resp = self.client.delete('/importer-api/data/%s' % upload_layers[0].id)
        self.assertEqual(resp.status_code, 301)
