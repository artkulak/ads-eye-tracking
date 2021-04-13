from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)

class Video(models.Model):
    video_link = models.CharField(max_length=200) # id of the vimeo webpage
    video_name = models.CharField(max_length=200) # name of video to display


class VideoStat(models.Model):
    '''
    Video stats storage
    '''
    video_link = models.CharField(max_length=200)
    user_id = models.CharField(max_length=200)
    timestamp = models.CharField(max_length=200)
    emotions = models.CharField(max_length=200)
    coordinates = models.CharField(max_length=200)
    screen_width = models.CharField(max_length=200)
    screen_height = models.CharField(max_length=200)
