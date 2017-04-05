#
# Tests that celery is running and tests
# Exchange Celery tasks.
#

from unittest import TestCase

from celery import Celery
import pytest

from exchange.core.models import CSWRecordForm
from exchange.tasks import create_new_csw

from . import ExchangeTest


class TestCelery(TestCase):

    def test_celery(self):
        # get a Celery "connection"
        celery = Celery()

        # This is a test task that returns the number
        # passed into the function.
        @celery.task
        def mirror(x):
            return x

        # some number.
        test_n = 44
        # kick off the celery task
        r = mirror.apply(args=(test_n,)).get()
        # ensure the number comes back.
        self.assertEqual(r, test_n)


class TestCSWRecord(ExchangeTest):

    @pytest.mark.skipif(settings.ES_UNIFIED_SEARCH is False,
                        reason="Only run if using unified search")
    @pytest.mark.celery(result_backend='rpc', broker_url='amqp://')
    def test_csw_insert(self):
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
            'contact_information': 'test@boundlessgeo.fake',
            'gold': '',
            'category': ''
        }

        form = CSWRecordForm(record)
        self.assertTrue(form.is_valid(), "Test record failed validation")

        new_record = form.save()
        new_record.save()
        create_new_csw.apply(args=(new_record.id,)).get()
