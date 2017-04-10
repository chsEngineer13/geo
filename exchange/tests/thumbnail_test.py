#
# Test Creation of Thumbnails.
#


from . import ExchangeTest

from StringIO import StringIO

class ThumbnailTest(ExchangeTest):

    def setUp(self):
        super(ThumbnailTest, self).setUp()

        self.login()

    def get_thumbnail(self, path):
        r = self.client.get(path)
        self.assertEqual(r.status_code, 200, "Failed to get thumbnail")
        return r

    def test_blank(self):
        r = self.client.get('/thumbnails/map/no-id')

        # TODO: should this really return a 404
        #       *and* a blank image?
        self.assertEqual(r.status_code, 200)

        # the blank gif has 43 characters in it. 
        self.assertEqual(len(r.content), 43, "This image does not appear to be blank")


    def test_basic_upload(self, img='test_thumbnail0.png'):
        global TEST_DIR

        test_legend_png = open(self.get_file_path(img), 'r')

        # post up a legend
        r = self.client.post('/thumbnails/map/0', 
                             {'thumbnail' : test_legend_png})

        # success!
        self.assertEqual(r.status_code, 201)

    def test_overwrite(self):
        # The legend should overwrite with the new image
        # without throwing an error.

        self.test_basic_upload()

        # yes, just do it again and see if the is an error
        self.test_basic_upload(img='test_thumbnail1.png')

        # and check that we have somehting more like test_thumbnail1.png

        r = self.get_thumbnail('/thumbnails/map/0');
        self.assertEqual(len(r.content), 4911, 'This does not look like thumbnail 1')

    def test_bad_image(self):

        # first a test without any thumbnail
        r = self.client.post('/thumbnails/map/0')
        self.assertEqual(r.status_code, 400, 'Tried to process a missing thumbnail.')

        # now a post with a *bad* thumbnail string.
        r = self.client.post('/thumbnails/map/0', {
            'thumbnail' : open(self.get_file_path('test_point.shp'), 'r')
        })
        self.assertEqual(r.status_code, 400, 'Tried to process a poorly formatted thumbnail.')


    def test_bad_object_type(self):
        r = self.client.post('/thumbnails/chicken/feed')
        self.assertEqual(r.status_code, 404)


    def test_huge_thumbnail(self):
        # thumbnails are limited in size, luckily we
        # can use a big random file since the size check happens
        # before the mimetype check.

        big_string = '*' * 400001

        r = self.client.post('/thumbnails/map/0', {
            'thumbnail' : StringIO(big_string)
        })

        self.assertEqual(r.status_code, 400)

