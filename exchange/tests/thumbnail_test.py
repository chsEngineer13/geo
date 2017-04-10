#
# Test Creation of Thumbnails.
#


from . import ExchangeTest

import os
import os.path

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class ThumbnailTest(ExchangeTest):

    def setUp(self):
        super(ThumbnailTest, self).setUp()

        self.login()

    def test_blank(self):
        r = self.client.get('/thumbnails/map/no-id')

        # TODO: should this really return a 404
        #       *and* a blank image?
        self.assertEqual(r.status_code, 200)

        # the blank gif has 43 characters in it. 
        self.assertEqual(len(r.content), 43, "This image does not appear to be blank")


    def test_basic_upload(self):
        global TEST_DIR

        test_legend_png = open(os.path.join(TEST_DIR, 'test_legend.png'), 'r')

        # post up a legend
        r = self.client.post('/thumbnails/map/0', 
                             {'thumbnail' : test_legend_png})

        # success!
        self.assertEqual(r.status_code, 201)
