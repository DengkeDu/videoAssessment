from ffmpeg import FFmpeg
import asyncio
import sys

resolution = ""
ffmpeg = FFmpeg(executable='/home/dengke/workdir/gpu/ffmpeg/ffmpeg')
@ffmpeg.on('progress')
def on_ffmpeg_progress(progress):
    if 'VMAF' in progress._fields:
        print(progress.VMAF)
    
ffmpeg.input(sys.argv[1])
ffmpeg.input(sys.argv[2])
ffmpeg.output("-",{'filter_complex':'libvmaf'},f="null")
loop = asyncio.get_event_loop()
loop.run_until_complete(ffmpeg.execute())
loop.close()