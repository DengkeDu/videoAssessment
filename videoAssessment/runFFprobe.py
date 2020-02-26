from ffmpeg import FFmpeg
import asyncio
import sys

resolution = ""
ffprobe = FFmpeg(executable='ffprobe')
@ffprobe.on('progress')
def on_ffprobe_progress(progress):
    print(progress.resolution)
    
ffprobe.input(sys.argv[1])
loop = asyncio.get_event_loop()
loop.run_until_complete(ffprobe.execute())
loop.close()