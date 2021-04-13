from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse


####################
# IMPORT OTHER LIBS
####################
import os
import numpy as np
import seaborn as sns
import cv2
from heatmappy import Heatmapper
from heatmappy.video import VideoHeatmapper
from PIL import Image
import moviepy.editor as mp
import urllib
import glob
import pandas as pd
from pathlib import Path
import shutil
import vimeo_dl as vimeo
import plotly.express as px
import plotly
import plotly.graph_objects as go

from .models import Video, VideoStat

EMOTIONS = [
    'angry', 
    'disgusted', 
    'fearful', 
    'happy', 
    'neutral', 
    'sad', 
    'surprised'
]

# # Create your views here.
# def index(request):
#     return render(request, 'index.html')

heatmap_points = []
def index(request):
    '''
    Renders login + main page
    '''
    global user
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            # if user is authentificated

            data = Video.objects.all()
            response_data = {
                "video_data": data,
                "name" : username,
                "is_staff": user.is_staff,
            }
            return render(request, 'main.html', response_data)
        return render(request, 'index.html')
    else:
        form = UserCreationForm()
    
    return render(request, 'index.html', {'form': form})


def video(request, video_id):
    '''
    Renders video page
    '''

    global video
    video = list(Video.objects.all())[video_id-1]

    VideoStat.objects.filter(video_link= video.video_link, user_id= user.username).delete()

    response_data = {
                "name" : user.username,
                "video_name": video.video_name,
                "video_link": video.video_link,
                "is_staff": user.is_staff
            }

        
    return render(request, 'video.html', response_data)

def calibrate(request):
    return render(request, 'calibration.html')


def recievePoints(request):
    '''
    Recieves gaze points via ajax request
    '''

    x, y = request.GET['x'], request.GET['y']
    time = request.GET['time']
    width, height = request.GET['width'], request.GET['height']
    username = request.GET['username']

    try:
        expressions = urllib.parse.unquote(request.GET['expressions']).split(';')
        expressions = list(map(float, expressions))
    except:
        expressions = []

    try:
        emotion = EMOTIONS[np.argmax(expressions)]
    except:
        emotion = 'None'
    

    try:
        x, y, time = int(float(x)), int(float(y)), int(float(time))
    except:
        x, y = 0, 0

    try:
        width, height = int(width), int(height)
    except:
        width, height = 0, 0


    VideoStat.objects.create(video_link= video.video_link, user_id= user.username, timestamp = time, emotions=emotion, coordinates=f'{x}:{y}', screen_width=width, screen_height=height)


    return JsonResponse({'ok': True})

def exportStats(request):
    '''
    Recieves export request via ajax
    '''
    # get video data
    entries = VideoStat.objects.filter(video_link=video.video_link)
    DOWNLOAD_PATH = Path('viewer/static/downloads') / video.video_link
    try:
        os.mkdir(DOWNLOAD_PATH)
    except:
        pass
        
    video_data = vimeo.new(f'https://vimeo.com/{video.video_link}')
    video_data.streams[0].download(quiet=False)
    video_width, video_height = str(video_data.streams[0]).split('@')[-1].split('x')
    video_width, video_height = int(video_width), int(video_height)

    # get video db entries
    heatmap_points = []
    emotion_points = []
    for e in entries:
        x,y = list(map(int, e.coordinates.split(':')))
        time = int(e.timestamp)

        x *= video_width / int(e.screen_width)
        y *= video_height / int(e.screen_height)
        heatmap_points.append([x,y, time])
        emotion_points.append([e.user_id, time//5000, e.emotions])
    
    emotions = pd.DataFrame(emotion_points)
    emotions.columns = ['user_name', 'timestamp', 'emotion']

    
    emotion_counts = []
    for (ts, item) in emotions.groupby('timestamp'):
        COUNTER = {
            'timestamp': item['timestamp'].iloc[0] * 5,
            'angry': 0, 
            'disgusted': 0, 
            'fearful': 0, 
            'happy': 0, 
            'neutral': 0, 
            'sad': 0, 
            'surprised': 0,
            'None': 0
        }
        for index, count in item['emotion'].value_counts().items():
            COUNTER[index] = count
        emotion_counts.append(COUNTER.values())
    emotion_counts = pd.DataFrame(emotion_counts)
    emotion_counts.columns = COUNTER.keys()
    emotion_counts.to_csv(DOWNLOAD_PATH / 'out.csv', index = None)

    
    heatmapper = Heatmapper(point_strength=0.6, opacity=0.8)
    video_heatmapper = VideoHeatmapper(heatmapper)
    heatmap_video = video_heatmapper.heatmap_on_video_path(
        video_path=f'{video_data.title}.mp4',
        points=heatmap_points
    )

    heatmap_video.write_videofile(str(DOWNLOAD_PATH / 'out.mp4'), bitrate="500k", fps=24)

    mp4_files = glob.glob(str('*.mp4'))
    for f in mp4_files:
        if f != 'out.mp4':
            os.remove(f)

    shutil.make_archive(str(DOWNLOAD_PATH), 'zip', str(DOWNLOAD_PATH))
    shutil.rmtree(str(DOWNLOAD_PATH))


    # time based graph

    fig = px.line(emotion_counts, x="timestamp", y=emotion_counts.columns[1:])
    fig = plotly.graph_objs.Figure(fig.data, fig.layout)
    fig_json_1 = fig.to_json()

    # pie chart
    labels, counts = list(emotions['emotion'].value_counts().index), list(emotions['emotion'].value_counts().values)
    fig = go.Figure(data=[go.Pie(labels=labels, values=counts)])
    fig_json_2 = fig.to_json()




    return JsonResponse({'ok': True, 'plotly_graph_1': fig_json_1, 'plotly_graph_2': fig_json_2})   
