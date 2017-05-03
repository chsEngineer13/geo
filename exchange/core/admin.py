from .models import CSWRecord

from django.contrib import admin, messages

from exchange.tasks import create_new_csw


def registry_insert(modeladmin, request, queryset):
    records_updated = 0
    for record in queryset:
        if record.status == 'Incomplete' or record.status == 'Error':
            create_new_csw.delay(record.id)
            records_updated += 1

    if records_updated > 0:
        messages.success(request, '{0} records submitted to Registry'.format(records_updated))

registry_insert.short_description = 'Register selected CSW Records'


class CSWRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'service_endpoint_url')
    list_filter = ('status', 'creator', 'record_type', 'category',)
    search_fields = ('title', 'abstract',)
    readonly_fields = ('status',)
    list_editable = ('category',)
    actions = [registry_insert]


admin.site.register(CSWRecord, CSWRecordAdmin)
