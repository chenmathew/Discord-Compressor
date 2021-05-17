import discord
from discord import File
import youtube_dl
import os
import os.path
import subprocess
import ffmpeg

def compress_video():
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe('video.mp4')
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    # Target total bitrate, in bps.
    target_total_bitrate = (65536000) / (1.073741824 * duration)

    # Target audio bitrate, in bps
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate
    video_bitrate = str(video_bitrate)
    subprocess.call(["ffmpeg", "-i", "video.mp4", "-vcodec", "h264", "-b:v", video_bitrate, "-acodec", "mp3" ,"-preset", "ultrafast", "output.mp4"])

client = discord.Client()

@client.event
async def on_ready():
  print('BOT IS ONLINE')

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if (message.content.startswith('https://vm.tiktok.com/') or message.content.startswith('https://twitter.com/')):
    ydl_opts = {'outtmpl': 'video.mp4'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([message.content])
    try:
        await message.channel.send(file=File("video.mp4"))
        pass
    except discord.HTTPException:
        compress_video()
        await message.channel.send(file=File("output.mp4"))
        pass
    if (os.path.isfile('video.mp4')):
        os.remove('video.mp4')
    if (os.path.isfile('output.mp4')):
        os.remove('output.mp4')
   
client.run('YOURTOKENHERE')
