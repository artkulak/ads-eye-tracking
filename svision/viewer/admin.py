from django.contrib import admin

# Register your models here.

from .models import Video, VideoStat

admin.site.register(Video)
admin.site.register(VideoStat)
