from django.db import models


class LoginEvent(models.Model):
    LOGIN = 0
    LOGOUT = 1
    FAILED = 2
    TYPES = (
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
        (FAILED, 'Failed login'),
    )
    event = models.SmallIntegerField(choices=TYPES)
    username = models.CharField(max_length=255, null=False, blank=False)
    ip = models.GenericIPAddressField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    superuser = models.NullBooleanField()
    staff = models.NullBooleanField()
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'login event'
        verbose_name_plural = 'login events'
        ordering = ['-datetime']
