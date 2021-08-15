# -*- coding: utf-8 -*-
"""
Created on Tue May 25 00:03:49 2021

@author: benja
"""

import pytube
import pydub
from pydub import AudioSegment
import os

url = 'https://www.youtube.com/watch?v=3ssL8vx7Xhg'
loc = 'C:\\Users\\benja\\Dropbox\\Uni\\PF\\Bums\\Klub100\\'


# Downloads overlay music for intro
youtube = pytube.YouTube(url)
musicOverlay = youtube.streams.filter(only_audio=True).first()
out = musicOverlay.download(loc)

os.rename(out,loc + 'overlay' + '.aac')
musicOverlay = AudioSegment.from_file(loc + 'overlay' + '.aac')

clipFile = '.m4a'
clipLoc = 'C:\\Users\\benja\\Dropbox\\Uni\\PF\\Bums\\Klub100\\Klip\\'
introOld = AudioSegment.from_file(clipLoc + 'introOld' + clipFile)

length = introOld.duration_seconds

musicOverlay = musicOverlay[0:length*1000]
musicOverlay = musicOverlay - 20
musicOverlay = musicOverlay.fade_out(2000)
introOld = introOld + 6

intro = introOld.overlay(musicOverlay, position=0)

intro.export(loc + 'intro' + clipFile)