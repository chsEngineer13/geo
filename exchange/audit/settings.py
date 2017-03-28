from django.conf import settings


AUDIT_TO_FILE = getattr(
    settings,
    'AUDIT_TO_FILE',
    False
)
AUDIT_LOGFILE_LOCATION = getattr(
    settings,
    'AUDIT_LOGFILE_LOCATION',
    'exchange_audit_log.json'
)
