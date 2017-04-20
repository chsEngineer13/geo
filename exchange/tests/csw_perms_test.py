#
# Ensure only administrative users can
# access the CSW views.
#

from . import ExchangeTest


class CswPermissionsTest(ExchangeTest):

    def _test_url(self, url, expectedStatus):
        r = self.client.get(url)
        self.assertEqual(r.status_code, expectedStatus,
                         'Mismatched status for %s. Expected %d, got %d' % (
                             url, expectedStatus, r.status_code
                         ))

    def test_as_test(self):
        # login as test.
        self.login(asTest=True)

        # should get a redirect to the authentication screen.
        self._test_url('/csw/new/', 302)
        self._test_url('/csw/status/', 302)
        self._test_url('/csw/status_table/', 302)

    def test_as_admin(self):
        # login as admin
        self.login()

        # these should all clear as 200s
        self._test_url('/csw/new/', 200)
        self._test_url('/csw/status/', 200)
        self._test_url('/csw/status_table/', 200)

    def test_menus_as_test(self):
        self.login(asTest=True)
        r = self.client.get('/')
        self.assertNotIn('/csw/new/', r.content, 'Found CSW Menu in Test User Login!')

    def test_menus_as_admin(self):
        self.login()
        r = self.client.get('/')
        self.assertIn('/csw/new/', r.content, 'No CSW Menu in Admin Login!')
