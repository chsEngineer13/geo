from django.contrib import admin
from . import models


class LoginEventAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super(LoginEventAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = [
        'datetime',
        'event',
        'username',
        'ip',
        'email',
        'fullname',
        'superuser',
        'staff'
    ]

    search_fields = ['username', 'ip', 'email', 'fullname']

    def __init__(self, *args, **kwargs):
        super(LoginEventAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

admin.site.register(models.LoginEvent, LoginEventAdmin)
