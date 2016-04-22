from django.contrib import admin
from solo.admin import SingletonModelAdmin
from exchange.models import SiteName, TagLine, BannerImage, IconImage, LogoImage, NavbarColor

admin.site.register(SiteName, SingletonModelAdmin)
admin.site.register(TagLine, SingletonModelAdmin)
admin.site.register(BannerImage, SingletonModelAdmin)
admin.site.register(IconImage, SingletonModelAdmin)
admin.site.register(LogoImage, SingletonModelAdmin)
admin.site.register(NavbarColor, SingletonModelAdmin)
