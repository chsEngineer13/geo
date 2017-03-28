from django.contrib.auth import signals as auth_signals, get_user_model
from .models import LoginEvent
from .settings import AUDIT_TO_FILE
from time import gmtime, strftime
from .utils import get_client_ip, write_entry

default = "not set"


# signals
def user_logged_in(sender, request, user, **kwargs):
    try:
        d = {
            "event": "login succesful",
            "event_time_gmt": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            "user_details": {
                "username": getattr(user, user.USERNAME_FIELD),
                "ip": get_client_ip(request),
                "superuser": user.is_superuser,
                "staff": user.is_staff,
                "full_name": user.get_full_name() or default,
                "email": user.email or default
            }
        }
        if AUDIT_TO_FILE:
            write_entry(d)
        login_event = LoginEvent(
            event=0,
            username=d['user_details']['username'],
            ip=d['user_details']['ip'],
            email=d['user_details']['email'],
            fullname=d['user_details']['full_name'],
            superuser=d['user_details']['superuser'],
            staff=d['user_details']['staff'],
        )
        login_event.save()
    except:
        pass


def user_logged_out(sender, request, user, **kwargs):
    try:
        d = {
            "event": "logout succesful",
            "event_time_gmt": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            "user_details": {
                "username": getattr(user, user.USERNAME_FIELD),
                "ip": get_client_ip(request),
                "superuser": user.is_superuser,
                "staff": user.is_staff,
                "full_name": user.get_full_name() or default,
                "email": user.email or default
            }
        }
        if AUDIT_TO_FILE:
            write_entry(d)
        login_event = LoginEvent(
            event=1,
            username=d['user_details']['username'],
            ip=d['user_details']['ip'],
            email=d['user_details']['email'],
            fullname=d['user_details']['full_name'],
            superuser=d['user_details']['superuser'],
            staff=d['user_details']['staff'],
        )
        login_event.save()
    except:
        pass


def user_login_failed(sender, credentials, **kwargs):
    try:
        user_model = get_user_model()
        d = {
            "gmtime": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            "event": "login failed",
            "username": credentials[user_model.USERNAME_FIELD],
        }
        if AUDIT_TO_FILE:
            write_entry(d)
        login_event = LoginEvent(
            event=2,
            username=d['username'],
        )
        login_event.save()
    except:
        pass

auth_signals.user_logged_in.connect(
    user_logged_in,
    dispatch_uid='audit_signals_logged_out'
)
auth_signals.user_logged_out.connect(
    user_logged_out,
    dispatch_uid='audit_signals_logged_out'
)
auth_signals.user_login_failed.connect(
    user_login_failed,
    dispatch_uid='audit_signals_login_failed'
)
