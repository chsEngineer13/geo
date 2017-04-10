from django.contrib import admin
from .models import Story


class StoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)

admin.site.register(Story, StoryAdmin)
