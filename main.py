from __future__ import unicode_literals
import discord
from discord import File
import asyncio
from flask import Flask
from threading import Thread
import itertools
from itertools import cycle
from discord.ext import commands, tasks
import youtube_dl
import os
import os.path
import subprocess
import ffmpeg


my_secret = os.environ['my secret']

app = Flask('')
status = itertools.cycle(['fr','sheeesh'])
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
 


@app.route('/')
def main():
  return "Your Bot Is Ready"

def run():
  app.run(host="0.0.0.0", port=8000)

def keep_alive():
  server = Thread(target=run)
  server.start()



client = discord.Client()

@client.event
async def on_ready():
  change_status.start()
  print('BOT IS ONLINE')

@tasks.loop(seconds=10)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.startswith('https://vm.tiktok.com/'):
    ydl_opts = {'outtmpl': 'video.mp4'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      ydl.download([message.content])
  if message.content.startswith('https://twitter.com/'):
    ydl_opts = {'outtmpl': 'video.mp4'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      ydl.download([message.content])
    await message.channel.send(file=File("video.mp4")) 
  if ((message.author.id == 836198988629278720) and (message.content.startswith('File too big.'))):
    await message.channel.send("mo daijoubu watashi ga kita")
    compress_video()
    await message.channel.send(file=File("output.mp4"))
    os.remove('video.mp4')
    os.remove('output.mp4')
   
keep_alive()
client.run(my_secret)