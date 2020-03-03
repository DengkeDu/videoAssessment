import json
from django.http import HttpResponse
from django.http import JsonResponse
import urllib.request
from ffmpeg import FFmpeg
import asyncio
from subprocess import Popen,PIPE
import os
import pyprobe
import logging

def assessment(request):
    loger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG,#控制台打印的日志级别
                    filename='new.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s'
                    #日志格式
                    )
    video_dict = {}
    res = {}
    video_json = request.body
    file1 = ""
    file2 = ""
    file2_scale = ""
    dl_file1 = ""
    dl_file2 = ""
    algorithms_type = ""
    parser = pyprobe.VideoFileParser(ffprobe="ffprobe", includeMissing=True, rawMode=False)
    try:
        video_dict = json.loads(video_json)
        if "file1" not in video_dict or "file2" not in video_dict:
            res["error"] = -4
            res["info"] = "file1 and file2 must be in body together"
            response = json.dumps(res)
            return HttpResponse(response)
        if "algorithms_type" not in video_dict:
            algorithms_type = "vmaf"
        else:
            algorithms_type = video_dict["algorithms_type"]
        file1 = video_dict["file1"]
        file2 = video_dict["file2"]
        loger.info(video_json)
        print(video_json)
        print("aaaaaaaaaaaaa")
    except Exception:
        res["error"] = -2
        res["info"] = "json loads failed"
        response = json.dumps(res)
        return HttpResponse(response)
    
    try:
        print(file1)
        dl_file1,headers = urllib.request.urlretrieve(file1)
        dl_file2,headers = urllib.request.urlretrieve(file2)
    except Exception:
        res["error"] = -3
        res["info"] = "file download failed"
        response = json.dumps(res)
        return HttpResponse(response)

    print(dl_file1)
    print(dl_file2)
    loger.info(dl_file1)
    loger.info(dl_file2)
    
    # Does the file type was video?
    try:
        file1_info = parser.parseFfprobe(dl_file1)
        file2_info = parser.parseFfprobe(dl_file2)
        loger.info(file1_info)
        loger.info(file2_info)
    except Exception:
        res["error"] = -5
        res["info"] = "file1 or file2 was not multimedia file"
        response = json.dumps(res)
        return HttpResponse(response)
    
    if "videos" not in file1_info or "videos" not in file2_info:
        res["error"] = -6
        res["info"] = "file1 or file2 was not video file"
        response = json.dumps(res)
        return HttpResponse(response)
    
    if len(file1_info['videos']) > 1 or len(file2_info['videos']) > 1:
        res["error"] = -7
        res["info"] = "file1 or file2 has more than one video stream, we support one video file, one video stream"
        response = json.dumps(res)
        return HttpResponse(response)
    
    
    # Get resolution
    # process = Popen(['python','videoAssessment/runFFprobe.py',dl_file1],stdout=PIPE,cwd=os.getcwd())
    # stdout,stderr = process.communicate()
    # file1_resolution = stdout.decode().rstrip()   
    # process = Popen(['python','videoAssessment/runFFprobe.py',dl_file2],stdout=PIPE,cwd=os.getcwd())
    # stdout,stderr = process.communicate()
    # file2_resolution = stdout.decode().rstrip()  
    file1_resolution = file1_info['videos'][0]['resolution']
    file2_resolution = file2_info['videos'][0]['resolution']
    
    file1_resolution = str(file1_resolution[0])+"x"+str(file1_resolution[1])
    file2_resolution = str(file2_resolution[0])+"x"+str(file2_resolution[1])
    
    print(file1_resolution)
    print(file2_resolution)
    loger.info(file1_resolution)
    loger.info(file2_resolution)
    
    # Scale file
    if file1_resolution != file2_resolution:
        loger.info("starting scale")
        process = Popen(['python','videoAssessment/runFFscale.py',dl_file2,file1_resolution],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        ret = stdout.decode().rstrip()
        if ret == "completed":
            file2_scale = dl_file2 +"_scale"
            loger.info(file2_scale)
        else:
            loger.info("%s scale to %s failed" % (file2,file2_resolution))
    else:
        file2_scale = dl_file2
        loger.info("No need to scale")
               
    if algorithms_type == "psnr":
        loger.info("runing psnr")
        process = Popen(['python','videoAssessment/runPSNR.py',dl_file1,file2_scale],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        s = stdout.decode()
        s=s.rstrip()
        res["type"] = "psnr"
        res["value"] = s
    elif algorithms_type == "vmaf":
        loger.info("runing vmaf")
        process = Popen(['python','videoAssessment/runVMAF.py',dl_file1,file2_scale],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        s = stdout.decode()
        s=s.rstrip()      
        res["type"] = "vmaf"
        res["value"] = s  
    elif algorithms_type == "ssim":
        loger.info("runing ssim")
        process = Popen(['python','videoAssessment/runSSIM.py',dl_file1,file2_scale],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        s = stdout.decode()
        s=s.rstrip()
        res["type"] = "ssim"
        res["value"] = s        
    if len(res) == 0:
        res["info"] = "Nothing"
    loger.info("Completed")
    loger.info(res)
    response = json.dumps(res)    
    return HttpResponse(response)
