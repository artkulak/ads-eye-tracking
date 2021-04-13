from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_panel/', admin.site.urls, name="admin_panel"),
    path('video/<int:video_id>', views.video, name='video'),
    path('recieve_points', views.recievePoints, name='recieve_points'),
    path('export_stats', views.exportStats, name='export_stats'),
    path('calibrate', views.calibrate, name='calibrate')
]