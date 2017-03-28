from django.apps import AppConfig


class ExchangeAuditConfig(AppConfig):
    name = 'exchange.audit'
    verbose_name = 'Audit Trail'

    def ready(self):
        import exchange.audit.signals  # noqa
