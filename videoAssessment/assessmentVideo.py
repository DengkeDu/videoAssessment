import json
from django.http import HttpResponse
from django.http import JsonResponse
import urllib.request
from ffmpeg import FFmpeg
import asyncio
from subprocess import Popen,PIPE
import os

def assessment(request):
    video_dict = {}
    res = {}
    video_json = request.body
    file1 = ""
    file2 = ""
    file2_scale = ""
    dl_file1 = ""
    dl_file2 = ""
    algorithms_type = ""
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
    
    # Get resolution
    process = Popen(['python','videoAssessment/runFFprobe.py',dl_file1],stdout=PIPE,cwd=os.getcwd())
    stdout,stderr = process.communicate()
    file1_resolution = stdout.decode().rstrip()   
    process = Popen(['python','videoAssessment/runFFprobe.py',dl_file2],stdout=PIPE,cwd=os.getcwd())
    stdout,stderr = process.communicate()
    file2_resolution = stdout.decode().rstrip()  
    
    # Scale file
    if file1_resolution != file2_resolution:
        process = Popen(['python','videoAssessment/runFFscale.py',dl_file2,file1_resolution],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        ret = stdout.decode().rstrip()
        if ret == "completed":
            file2_scale = dl_file2 +"_scale"
            print(file2_scale)
        else:
            print("%s scale to %s failed" % (file2,file2_resolution))
    else:
        file2_scale = dl_file2
        print("No need to scale")
               
    if algorithms_type == "psnr":
        process = Popen(['python','videoAssessment/runPSNR.py',dl_file1,file2_scale],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        s = stdout.decode()
        s=s.rstrip()
        res["PSNR"] = s
    elif algorithms_type == "vmaf":
        process = Popen(['python','videoAssessment/runVMAF.py',dl_file1,file2_scale],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        s = stdout.decode()
        s=s.rstrip()        
        res["VMAF"] = s
    elif algorithms_type == "ssim":
        process = Popen(['python','videoAssessment/runSSIM.py',dl_file1,file2_scale],stdout=PIPE,cwd=os.getcwd())
        stdout,stderr = process.communicate()
        s = stdout.decode()
        s=s.rstrip()        
        res["SSIM"] = s        
    
    response = json.dumps(res)
    return HttpResponse(response)
