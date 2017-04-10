from django.contrib import admin
from .models import Story, StoryChapter


class StoryMapRelationshipInline(admin.TabularInline):
    model = StoryChapter
    extra = 1


class StoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    inlines = (StoryMapRelationshipInline,)

admin.site.register(Story, StoryAdmin)


