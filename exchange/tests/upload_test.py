# Perform tests against the uploader.
#
#


import json
import re
import time

from . import ExchangeTest

import pytest

from exchange import settings


# This is a dummy exception class
#  used to make back tracing easier.
class UploaderException(Exception):
    pass


# Sift through the HTML for the Javascript defined
#  bounding box.
def parse_bbox_from_html(html):
    p = re.compile('"bbox": ' +
                   '\[([0-9\-\.]+), ([0-9\-\.]+), ' +
                   '([0-9\-\.]+), ([0-9\-\.]+)\]')

    bboxes = p.findall(html)

    if(len(bboxes) > 0):
        return [float(x) for x in bboxes[0]]
    return None


class TestBBOXParser(ExchangeTest):

    def test_invalid_bbox(self):
        self.assertIsNone(parse_bbox_from_html(''),
                          'BBOX parser failed to fail properly')


class UploaderMixin:
    # Upload a shapefile and create a new layer.
    #
    # @params {dict} files Keys are the form names,
    #                   Values are the paths to the files.
    # @params {dict} uploaderParams Extra parameters to change
    #                               the behaviour of theupload.
    #
    # TODO : Permissions options.
    #
    # @return The info for the layer as a dict.
    def upload_shapefile(self, files, uploaderParams={}):
        params = {
            'geogig': 'false',
            'geogig_store': '',
            'time': 'false',
            'permissions': '{"users":{"AnonymousUser":[]},"groups":{}}',
            'charset': 'UTF-8',
        }

        for f in files:
            params[f] = open(self.get_file_path(files[f]), 'rb')

        # mixin the uploader params into the request.
        params.update(uploaderParams)

        post_r = self.client.post('/upload/', params, follow=True)

        self.assertEqual(post_r.status_code, 200)

        layer_info = json.loads(post_r.content)

        # The upload handler works by sending repeated messages with a
        #  "redirect_to" attribute.  This starts the chain going
        #  and the while loop below keeps following it.
        layer_info['redirect_to'] += '&force_ajax=true'
        next_step = layer_info

        while('redirect_to' in next_step):
            next_r = self.client.get(next_step['redirect_to'])
            next_step = {}
            if(next_r.status_code == 200):
                next_step = json.loads(next_r.content)
            time.sleep(3)

        # If the last "step" did not produce a url
        #  then raise an excpetion that the layer upload
        #  must've failed.
        if('url' not in next_step):
            raise UploaderException("Failed to upload new layer")

        return next_step

    # Remove a layer from the list.
    #
    # @param uri       Uri to the layer info, appends 'remove' to the end.
    #
    def drop_layer(self, uri=None):
        working_uri = uri + '/remove'
        drop_r = self.client.post(working_uri, follow=False)
        self.assertEqual(drop_r.status_code, 302,
                         "Did not return expected forwaring code!")


# Test class for uploading layer
#
# Performs various uploads and drops of layers.
#
@pytest.mark.skipif(True or settings.ES_SEARCH is False,
                    reason="Only run if using unified search")
class UploadLayerTest(UploaderMixin, ExchangeTest):

    def setUp(self):
        super(UploadLayerTest, self).setUp()
        self.login()

    # This is a meta function for executing uploader options.
    #
    # Uploads the shapefile, checks on the layer, and drops it.
    #
    def _test_meta(self, shapefile, uploaderParams={}):
        layer_uri = self.upload_shapefile(shapefile).get('url', None)
        if(layer_uri is not None):
            self.drop_layer(uri=layer_uri)

    # Test an upload to geogig of a basic single-point shapefile.
    #
    def test_geogig_upload(self):
        data_path = './test_point.'
        shapefile = [data_path + x for x in ['prj', 'shp', 'shx', 'dbf']]

        shapefile = {
            'base_file': data_path + 'shp',
            'dbf_file': data_path + 'dbf',
            'shx_file': data_path + 'shx',
            'prj_file': data_path + 'prj'
        }

        params = {
            'geogig': 'true',
            'geogig_store': 'NoseTests'
        }

        self._test_meta(shapefile, uploaderParams=params)

    # Test the uploading of a shapefile contained in a zip-file
    #
    def test_zip_upload(self):
        shapefile = {
            'base_file': './test_point.zip'
        }

        self._test_meta(shapefile)

    # Test uploading a basic geojson file.
    # 20 March 2017: Test being skipped as not all uploaders
    #                support GeoJson
    def _test_geojson_upload(self):
        shapefile = {
            'base_file': './bbox.geojson'
        }
        self._test_meta(shapefile)

    # Test the BBOX of a layer when it's been uploaded to GeoGig
    #  against when it has not been uploaded to GeoGig.
    #
    # Refs: NODE-804
    def test_bbox_issues(self):
        data_path = './bbox.'

        shapefile = {
            'base_file': data_path + 'shp',
            'dbf_file': data_path + 'dbf',
            'shx_file': data_path + 'shx',
            'prj_file': data_path + 'prj'
        }

        params = {
            'geogig': 'true',
            'geogig_store': 'NoseTests'
        }

        geogig_layer = self.upload_shapefile(shapefile, params)
        geogig_layer_uri = geogig_layer.get('url', None)

        # ensure the url exists
        self.assertIsNotNone(geogig_layer_uri,
                             "Bad URI for geogig layer")

        # get the layer data
        geogig_layer_info = self.client.get(geogig_layer_uri)

        # ensure "GeoGig" exists in the layer
        self.assertIn('GeoGig', geogig_layer_info.content)

        # pull the BBOX out of the Geogig layer
        geogig_bbox = parse_bbox_from_html(geogig_layer_info.content)

        self.assertIsNotNone(geogig_bbox,
                             "No bounding box found in Geogig Layer!")

        # second time around, no GeoGig
        params = {
            'geogig': 'false',
            'geogig_store': ''
        }

        layer_uri = self.upload_shapefile(shapefile, params).get('url', None)
        self.assertIsNotNone(layer_uri, "Failed to get valid layer_uri!")
        layer_info = self.client.get(layer_uri)
        self.assertNotIn('GeoGig', layer_info.content)

        bbox = parse_bbox_from_html(layer_info.content)

        self.assertIsNotNone(bbox,
                             "No bounding box found in non-Geogig Layer!")

        # convert the bounding boxes to strings
        #  for reporting
        s_geogig_bbox = ','.join(str(x) for x in geogig_bbox)
        s_bbox = ','.join(str(x) for x in bbox)

        # the bounding boxes are reprojected from 4326 to 3857,
        #  if the bboxes are within a metre of each other then that's a
        #  close enough match to satisfy the test.
        for i in range(4):
            t = geogig_bbox[i] - bbox[i]
            self.assertTrue(-1 <= t and t <= 1,
                            "Mismatched bounding Boxes! %s (geogig) != %s" % (
                                s_geogig_bbox, s_bbox
                            ))


@pytest.mark.skipif(settings.ES_SEARCH is False,
                    reason="Only run if using unified search")
class NonAdminUploadTest(UploaderMixin, ExchangeTest):

    def setUp(self):
        super(UploadLayerTest, self).setUp()
        # test user is not an admin
        self.login(asTest=True)

    # This is a meta function for executing uploader options.
    #
    # Uploads the shapefile, checks on the layer, and drops it.
    #
    def _test_meta(self, shapefile, uploaderParams={}):
        layer_uri = self.upload_shapefile(shapefile).get('url', None)
        if(layer_uri is not None):
            self.drop_layer(uri=layer_uri)

    # Test an upload to geogig of a basic single-point shapefile.
    #
    def test_geogig_upload(self):
        data_path = './test_point.'
        shapefile = [data_path + x for x in ['prj', 'shp', 'shx', 'dbf']]

        shapefile = {
            'base_file': data_path + 'shp',
            'dbf_file': data_path + 'dbf',
            'shx_file': data_path + 'shx',
            'prj_file': data_path + 'prj'
        }

        params = {
            'geogig': 'true',
            'geogig_store': 'NoseTests'
        }

        self._test_meta(shapefile, uploaderParams=params)
