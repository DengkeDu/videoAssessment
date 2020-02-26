from ffmpeg import FFmpeg
import asyncio
import sys

resolution = ""
ffmpeg = FFmpeg(executable='ffmpeg')
@ffmpeg.on('progress')
def on_ffmpeg_progress(progress):
    if 'PSNR' in progress._fields:
        print(progress.PSNR)
    
ffmpeg.input(sys.argv[1])
ffmpeg.input(sys.argv[2])
ffmpeg.output("-",{'filter_complex':'psnr'},f="null")
loop = asyncio.get_event_loop()
loop.run_until_complete(ffmpeg.execute())
loop.close()