from django.test import TestCase
from exchange.tasks import create_new_csw
from exchange.core.models import CSWRecord
import pytest
from django.conf import settings

@pytest.mark.skipif(settings.REGISTRYURL is None,
                    reason="Only run if registry configured")
class CreateNewCSWTest(TestCase):

    def setUp(self):
        rec = CSWRecord.objects.create(
            title='foo',
            creator='me',
            modified='2017-01-01',
            source='http://foo.com'
        )
        rec.save()
        self.record_id = rec.id

    def test(self):
        create_new_csw(self.record_id)
        rec = CSWRecord.objects.get(id=self.record_id)
        self.assertEqual(
            rec.status,
            'Complete'
        )
