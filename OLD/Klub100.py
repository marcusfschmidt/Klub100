#Imports and functions
pass
import pytube
import pandas as pd
from pydub import AudioSegment
import numpy as np
import os
import sheets
import urllib.request

#Normalise sound volume
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

#Load soundclip and normalise
def loadSoundClip(loc,sound,normVol):
    soundClip = AudioSegment.from_file(loc+sound)
    soundClip = match_target_amplitude(soundClip, normVol)
    return soundClip

#Boolean to check for internet connection
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False


#%%

randomSeedSeed = np.random.randint(0,10000)
randomSeed = 749

normVol = -5

loc = 'C:\\Users\\Marcus\\OneDrive - Danmarks Tekniske Universitet\\k100\\'
songLoc = loc + "sange\\"
songFile = '.aac'

fuck = loc+"kwabs.aac"
bundPath = loc + "bund.m4a"
outroPath = loc+"outro.m4a"


qwabs = loadSoundClip(loc, "kwabs.aac", normVol)
hello = loadSoundClip(loc, "hello.mp3", normVol)
intro = loadSoundClip(loc, "intro.m4a", normVol)



turbomode = AudioSegment.from_file(loc+"turbomode.m4a")
skildpadde = AudioSegment.from_file(loc+"skildpadde.m4a")
mashup = AudioSegment.from_file(loc+"mashup.m4a")
clip = AudioSegment.from_file(fuck)
outro = AudioSegment.from_file(outroPath)



hello = match_target_amplitude(hello, normVol)
intro = match_target_amplitude(intro, normVol)
turbomode = match_target_amplitude(turbomode, normVol)
clip = match_target_amplitude(clip, normVol)
outro = match_target_amplitude(outro, normVol)
skildpadde = match_target_amplitude(skildpadde, normVol)
mashup = match_target_amplitude(mashup, normVol)


if connect():
    print("Gathering songs from Google Sheets.")
    data = sheets.klubhest()
else:
    print("Gathering songs from local Excel file.")
    file = 'C:\\Users\\Marcus\\OneDrive - Danmarks Tekniske Universitet\\k100\\k100.xlsx'
    print(file)
    # Reads data in excel file 
    data = pd.read_excel(file)
    
    
url = data.loc[:,'Link']
startSec = data.loc[:,'Starttid i sang [s]'].astype('int')
songName = data.loc[:,'Sang']
    

bundarray = np.empty(8,dtype=object)
for i in range(8):
    bund = AudioSegment.from_file(loc + "bund{}.m4a".format(i+1))
    bund = match_target_amplitude(bund, normVol)
    bundarray[i] = bund
    
patarray = np.empty(5,dtype=object)
for i in range(5):
    pat = AudioSegment.from_file(loc + "pat{}.m4a".format(i+1))
    pat = match_target_amplitude(pat, normVol)

    patarray[i] = pat
    
#%%

# Defines the output file
BumsernesKlub100 = AudioSegment.empty()
BumsernesKlub100 += intro


def pois(mean,seed=None):
    out = 0
    while out == 0:
        np.random.seed(seed)
        out = np.random.poisson(mean)
        
        if type(seed) == np.int32 and out == 0:
            seed += 1
    
    return out


def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)
      })
     # convert the sound with altered frame rate to a standard frame rate
     # so that regular playback programs will work right. They often only
     # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

    

def randomqwabs(clip,mean,speedLow,speedHigh,maxtime,seed=None):
    number = pois(mean,seed+1)
    
    np.random.seed(seed)
    speeds = np.random.uniform(speedLow,speedHigh,number)
    
    hestetal = clip.duration_seconds
    # if helloBool:
    #     hestetal = 
    # else:
    #     hestetal = 3
    loopnumber = np.int(np.ceil(maxtime/(speedLow*hestetal)))
    
    cliplist = np.empty(number,dtype=object)
    # Loop loopnumber of times
    for i in range(number):
        cliplist[i] = AudioSegment.empty()

        for j in range(loopnumber):
            cliplist[i] += clip
            
    # Change speeds
    
    for k in range(number):
        cliplist[k] = speed_change(cliplist[k],speeds[k])

        
    #overlay from the list of clips
    clipOut = cliplist[0]
    
    if number > 1:
        
        for i in range(1,number):
            clipOut = clipOut.overlay(cliplist[i],position=0)
            
            
    clipOut = clipOut[0:maxtime*1000]
            
    
    return clipOut,min(speeds)


def randomBundClip(bundarray,seed=None):
    np.random.seed(seed)
    randomNumber = np.random.randint(0,len(bundarray))
    return bundarray[randomNumber]

def lowerVolumeInterval(clip,start,end,db):
    
    song1 = clip[0:start]
    song2 = clip[start:end]
    song3 = clip[end:-1]
    
    song2 = song2 + db
    
    song1 += song2
    song1 += song3
    return song1

#%%
#Download sange

print("Downloading any missing songs out of {}".format(len(url)) + " in total.")
for i in range(len(url)):

    # Renames the song
    new = songName[i] 
    if os.path.isfile(songLoc + new + songFile) == False:
        print("Downloading song " + new + ", {}".format(i+1)+" out of "+str(len(url)))
        # Downloads the youtube audio
        youtube = pytube.YouTube(url.loc[i])
        song = youtube.streams.filter(only_audio=True).first()
        out = song.download(songLoc)
        os.rename(out,songLoc + new + songFile)
        
        
        
    # else:
    #     print("Song {}".format(i+1)+" out of "+str(len(url))+", "+ new+", already downloaded, ")
print("æøæøæøæøæøæøøææøøæøæ bund")
print("done with downloading songs hello")
# %%

np.random.seed(randomSeed)
seeds = np.random.randint(0,99999999,20000)

np.random.seed(seeds[0])
randomSongsList = np.random.choice(len(url),len(url),replace=False)

np.random.seed(seeds[1])
randomQwabs = np.random.randint(0,100)

np.random.seed(seeds[2])
randomturbo = np.random.randint(5,11)

np.random.seed(seeds[3])
turbolist = np.random.randint(0,100,randomturbo)

np.random.seed(seeds[4])
randompadde = np.random.randint(5,11)

np.random.seed(seeds[5])
paddelist = np.random.randint(0,100,randompadde)

print("\nNow stitching the songs...")

i = 0
songcounter = 1
while songcounter <= 100:
    new = songName[i]
    song = AudioSegment.from_file(songLoc + new + songFile)
    song = match_target_amplitude(song, normVol)
    # Defines the starttime and the endtime of the song
    startTime = startSec[i]*1000
    endTime = startTime+60*1000
    # Applies the new times of the song
    songNew = song[startTime:endTime]

    # Adds fade in and fade out to the song
    songNew = songNew.fade_in(2000).fade_out(2000)
    
    np.random.seed(seeds[6+i*100])
    chance = np.random.random()
    
    np.random.seed(seeds[7+i*100])
    hellochance = np.random.random()
    
    np.random.seed(seeds[8+i*100])
    mashupchance = np.random.random()
    
    
    randomHelloBool = False
    randomQwabsBool = False
          
    
    if chance <= 0.33:
        np.random.seed(seeds[9+i*100])
        ranposqwabs = np.random.randint(0,50*1000)
        
        np.random.seed(seeds[10+i*100])
        maxtime = np.random.randint(1,8)
        slowest = clip.duration_seconds/maxtime
        
        ranqwbs,sonic = randomqwabs(clip,3,slowest,2,maxtime,seeds[11+i*100])
        ranqwbs = ranqwbs+6
        songNew = songNew.overlay(ranqwbs,position=ranposqwabs)
        if sonic < 0.33:
           pos = ranposqwabs+maxtime*1000+0.5*1000
           
           bundclip = randomBundClip(bundarray,seeds[12+i*100])
           
           timeend = np.int(bundclip.duration_seconds*1000)+pos
           songNew = lowerVolumeInterval(songNew,pos,timeend,-13)
           songNew = songNew.overlay(bundclip+10,position=pos)
           
        randomQwabsBool = True
        
    if hellochance <= 0.15:
        np.random.seed(seeds[13+i*100])
        ranposhello = np.random.randint(0,50*1000)
        
        np.random.seed(seeds[14+i*100])
        maxtime = np.random.randint(1,7)
        
        slowest = hello.duration_seconds/maxtime
        ranhello,AAAAA = randomqwabs(hello,4,slowest,1.5,maxtime,seeds[15+i*100])
        ranhello = ranhello+6
        songNew = songNew.overlay(ranhello,position=ranposhello)
        randomHelloBool = True
        
    
    if randomQwabsBool and randomHelloBool:
        
        bundposition = max(ranposhello,ranposqwabs)
        pos = bundposition+maxtime*1000+0.5*1000
        
        bundclip = randomBundClip(bundarray,seeds[16+i*100])
        timeend = np.int(bundclip.duration_seconds*1000)+pos
        songNew = lowerVolumeInterval(songNew,pos,timeend,-13)
        songNew = songNew.overlay(bundclip+10,position=pos)

    
    np.random.seed(seeds[17+i*100])
    mean = np.random.randint(3,11)
    
    np.random.seed(seeds[18+i*100])
    maxtime = np.random.randint(6,11)
        
    
    pause,AAAAAAA = randomqwabs(clip,mean,0.2,2,maxtime,seeds[19+i*100])
    # Adds song and clip to the output file, except for the first clip
    if i > 0:
        if new == "cat":
            kat = AudioSegment.from_file(loc + "\\kat.m4a")
            kat += songNew
            BumsernesKlub100 += kat
        else:
            BumsernesKlub100 += pause
            
            
    if i in turbolist and i in paddelist:
        FUCK = AudioSegment.empty()
        FUCK += turbomode
        FUCK = FUCK.overlay(skildpadde,position=0)
        FUCKpos = FUCK.duration_seconds
        
        FUCK += songNew
        
        turbobundarr = np.empty(2,dtype=object)
        for k in range(2):
            bundehest,ssas = randomqwabs(bundarray[k],1,0.5,1.3,60,seed=seeds[22+i*100])
            turbobundarr[k] = bundehest
            
            
        #overlay from the list of clips
        turbobund = turbobundarr[0]
            
        for k in range(1,2):
            turbobund = turbobund.overlay(turbobundarr[k],position=0)
        
            
        
        
        FUCK = FUCK.overlay(turbobund-3,position=FUCKpos*1000)
        
        songNew = FUCK
            
        
    elif i in turbolist:
        hestesang = AudioSegment.empty()
        songNew = speed_change(songNew,2)
        
        hestesang += turbomode
        hestesang += songNew
        songNew = hestesang    
        
    elif i in paddelist:
       hestesang = AudioSegment.empty()
       songNew = speed_change(songNew,0.5)
       
       hestesang += skildpadde
       hestesang += songNew
       songNew = hestesang
       
       
       
        
    helmigboolean = False
    mashupboolean = False
    
    if new == "helmig":
        helmigboolean = True
        
    if mashupchance <= 0.02 and i < len(url):
        nameB = songName[i+1] 
        songB = AudioSegment.from_file(songLoc + nameB + songFile)
        songB = match_target_amplitude(songB, normVol)

        # Defines the starttime and the endtime of the song
        startTime = startSec[i+1]*1000
        endTime = startTime+60*1000
        # Applies the new times of the song
        songNewB = songB[startTime:endTime]
    
        # Adds fade in and fade out to the song
        songNewB = songNewB.fade_in(2000).fade_out(2000)
        
        if nameB == "helmig":
                helmigboolean = True
            
        songNew = songNew.overlay(songNewB,position=0)
        joke = AudioSegment.empty()
        joke += mashup
        joke += songNew
        
        songNew = joke
        mashupboolean = True
        
        
    if helmigboolean:
        posarray = np.array([30500,36500,42500,48000,53500])
        for j in range(5):
            songNew = songNew.overlay(patarray[j]+10,position=posarray[j])
        
   
    if mashupboolean:
        i += 2
    else:
        i += 1
        
    songcounter += 1
    
    if i == randomQwabs:            
        waeoe,AAAAAAA = randomqwabs(clip,15,0.2,2,60,seeds[21+i*100])
        
        if mashupboolean:
            songNew = songNew.overlay(waeoe,position=0)
        else:
            songNew = waeoe
            
        songNew = songNew.fade_in(2000).fade_out(2000)
        songNew = match_target_amplitude(songNew, normVol)
        
    BumsernesKlub100 += songNew
    print('Qwabs100 is at song',songcounter-1,'out of 100')

# Adds the outro file to the output file
BumsernesKlub100 += outro

# Exports the output file
BumsernesKlub100.export(loc + 'BumsernesKlub100_seed{}'.format(randomSeed) + '.wav')
print('Seed used was {}'.format(randomSeed))
print('bonsjuar madame')

