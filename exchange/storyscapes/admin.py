from django.contrib import admin
from .models.base import Story, StoryChapter
from .models.frame import Frame
from .models.marker import Marker


class StoryMapRelationshipInline(admin.TabularInline):
    model = StoryChapter
    extra = 1


class StoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    inlines = (StoryMapRelationshipInline,)


class FrameAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    #list_filter = ('map',)
    search_fields = ('title', 'description',)


class MarkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    #list_filter = ('map',)
    search_fields = ('title', 'description',)


admin.site.register(Marker, MarkerAdmin)
admin.site.register(Frame, FrameAdmin)
admin.site.register(Story, StoryAdmin)


