import json
from .settings import AUDIT_LOGFILE_LOCATION


def write_entry(d):
    with open(AUDIT_LOGFILE_LOCATION, 'a') as j:
        json.dump(d, j, sort_keys=True)
        j.write('\n')
        j.close()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
