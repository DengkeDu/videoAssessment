import json
from django.http import HttpResponse
from django.http import JsonResponse
import urllib.request
from ffmpeg import FFmpeg
import asyncio

resolution = ""

ff = FFmpeg()
@ff.on('progress')
def on_ff_progress(progress):
    print(progress)

ffprobe = FFmpeg(executable='ffprobe')
@ffprobe.on('progress')
def on_ffprobe_progress(progress):
    print(progress)
    resolution = progress.resolution

def assessment(request):
    video_dict = {}
    res = {}
    video_json = request.body
    file1 = ""
    file2 = ""
    dl_file1 = ""
    dl_file2 = ""
    try:
        #video_dict = json.loads(video_json)
        #file1 = video_dict["file1"]
        #file2 = video_dict["file2"]
        print(video_json)
        print("aaaaaaaaaaaaa")
    except Exception:
        res["error"] = -2
        response = json.dumps(res)
        return HttpResponse(response)
    try:
        dl_file1,headers = urllib.request(file1)
        #dl_file2,headers = urllib.request(file2)
        ffprobe.input(dl_file1)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ffprobe.execute())
        loop.close   
        res['resolution'] = resolution
        
    except Exception:
        res["error"] = -3
        response = json.dumps(res)
        return HttpResponse(response)
    response = json.dumps(res)
    return HttpResponse(response)
