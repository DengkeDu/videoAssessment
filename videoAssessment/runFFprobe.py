from ffmpeg import FFmpeg
import asyncio
import sys

resolution = ""
ffprobe = FFmpeg(executable='ffprobe')
@ffprobe.on('progress')
def on_ffprobe_progress(progress):
    if 'resolution' in progress._fields:
        resolution = progress.resolution.replace("\n","").replace("\r","")
        print(resolution)
    
ffprobe.input(sys.argv[1])
loop = asyncio.get_event_loop()
loop.run_until_complete(ffprobe.execute())
loop.close()