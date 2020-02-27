from ffmpeg import FFmpeg
import asyncio
import sys

ffscale = FFmpeg()
@ffscale.on('completed')
def on_complete():
    print("completed")

# @ffscale.on('progress')
# def on_ffprobe_progress(progress):
#     print(progress.resolution)

new_file = sys.argv[1] + "_scale"
filter_scale = "scale=" + sys.argv[2]

ffscale.input(sys.argv[1])
ffscale.output(new_file,{'filter_complex':filter_scale},f='mp4')
loop = asyncio.get_event_loop()
loop.run_until_complete(ffscale.execute())
loop.close()
