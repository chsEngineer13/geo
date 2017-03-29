# Perform tests for auditing.
#
#
from . import ExchangeTest
from exchange.audit.models import LoginEvent

class AuditTest(ExchangeTest):

    def test(self):
        self.login()
        last_event = LoginEvent.objects.latest('datetime')
        self.assertEquals(last_event.event,0)
        self.client.logout()
        last_event = LoginEvent.objects.latest('datetime')
        self.assertEquals(last_event.event,1)
        self.client.login(
            username='bogus',
            password='bogus'
        )
        last_event = LoginEvent.objects.latest('datetime')
        self.assertEquals(last_event.event,2)