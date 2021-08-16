import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import pytube
import pandas as pd
from pydub import AudioSegment
import numpy as np
import glob
import sheets
import urllib.request

#Klub100 class 
class Klub100(object):
    
    def __init__(self,loc,normVol,length=100,seed=None,localBool=False):
        print("Initialising Klub100.\n")
        
        #Initialise parameters
        #Root folder location
        self.loc = loc
        
        #Normalised volume in dBFS
        self.normVol = normVol
        
        self.songs = []
        self.positions = []
        
        #Length of klub100 :)
        self.length = length
        self.seed = np.random.randint(0,100000) if seed is None else seed
        
        np.random.seed(self.seed)
        self.seeds = np.random.randint(0,99999999,20000)
        
        #Arrays to hold settings for custom effects
        self.songOverlaySettings = []
        self.songOverlayBooleans = {}
        
        #Read and download songs locally or from Sheets
        url, startSec, songName = self.readSongs(loc, localBool)
        self.downloadSongs(loc,url,startSec,songName,normVol)
        
        self.url = url
        self.startSec = startSec
        self.songName = songName
        
        eLoc = loc + "effects\\"
        print("\nReading sound effects from directory\n" + eLoc)
        self.effects = self.readSoundEffects(loc + "effects\\",normVol)
        print("Finished reading sound effects.")
        
        
    def randomInt(self,seed,minimum=0,maximum=99999999,size=20000):
        np.random.seed(seed)
        return np.random.randint(minimum,maximum,size)
    
    def randomFloat(self,seed,size=1):
        np.random.random(seed)
        return np.random.random(size)
    
    #Zero-truncated poisson distribution
    def pois(self,mean,seed):
        out = 0
        while out < 1:
            np.random.seed(seed)
            out = np.random.poisson(mean)
            
            if type(seed) == np.int32 and out == 0:
                seed += 1
        return out
    
    #Boolean to check for internet connection
    def connect(self,host='http://google.com'):
        try:
            urllib.request.urlopen(host) #Python 3.x
            return True
        except:
            return False
        
        
  # Functions to read songs from Sheets or a local Excel file   
    def readSongs(self,loc,localBool):
        
        if localBool == False:
            if self.connect():
                print("Gathering songs from Google Sheets.")
                data = sheets.klubhest(loc)
            else: 
                print("Attempted to gather songs from Google Sheets, but you are not connected to the internet. Gathering from local file instead.")
                print(loc+ "k100.xlsx")
                # Reads data in excel file 
                data = pd.read_excel(loc + "k100.xlsx")
        else:
            print("Gathering songs from local Excel file.")
            print(loc+ "k100.xlsx")
            # Reads data in excel file 
            data = pd.read_excel(loc + "k100.xlsx")
            

        
        url = data.loc[:,'Link']
        songName = data.loc[:,'Sang']
        nullIndex = np.where(pd.isnull(data.loc[:,'Starttid i sang [s]']))[0]
        if len(nullIndex) > 0:
            data.loc[:,'Starttid i sang [s]'][nullIndex] = 0
        startSec = data.loc[:,'Starttid i sang [s]'].astype('int')
            
        return url, startSec, songName  


    #If there are more downloaded songs than read from self.readSoungs(), this function is run
    def compareFiles(self,songLoc,songsFromDataFrame):
        fileList = glob.glob(songLoc+'\*.*')
        filenames = self.readFileNames(songLoc, fileList)
        
        if self.connect():
            print("No missing songs, but the number of local songs exceed the number of songs in Google Sheets. Has something gone wrong?\n")
        else:
            print("No missing songs, but the number of local songs exceed the number of songs in the local .xlsx file. Attempt to gain internet connection and synchronize with the Google sheets, as the generated Klub100 will only use entries in the Google Sheets or the local .xlsx-file.\n")

        for file in filenames:
                if file not in songsFromDataFrame.tolist():
                    if self.connect():
                        print("'" +file+".mp4'" + " is available locally but not in Google Sheets.")
                    else:
                        print("'" +file+".mp4'" + " is available locally but not in the local .xlsx-file.")

       

    #Download songs using Google Sheets API (if internet) or using a local Excel
    def downloadSongs(self,loc,url,startSec,songName,normVol):
        #Define the song location
        songLoc = loc + "songs\\"
        
        #dict.fromkeys to remove duplicate values
        numberOfSongs = len(dict.fromkeys(url))
        numberOfMissingSongs = numberOfSongs-len(glob.glob(songLoc+'*.*'))
            
        if numberOfMissingSongs > 0:
            print("Downloading {} missing song(s) out of {}".format(numberOfMissingSongs,numberOfSongs) + " in total.")
            for i in range(len(url)):
                # Renames the song
                if os.path.isfile(songLoc + songName[i] + '.mp4') == False:
                    print("Downloading song " + songName[i] + ", {}".format(i+1)+" out of "+str(len(url)))
                    try:
                        # Downloads the youtube audio
                        youtube = pytube.YouTube(url.loc[i])
                        song = youtube.streams.get_audio_only()
                        out = song.download(songLoc)
                        os.rename(out,songLoc + songName[i] + '.mp4')
                        
                        #Only save the minute needed for the final klub100
                        song = self.loadSoundClip(songLoc+songName[i]+'.mp4',normVol)
                        startTime = startSec[i]*1000
                        endTime = startTime+60*1000
                        song = song[startTime:endTime]
                        song.export(songLoc + songName[i] + '.mp4',format="mp4")
                    except:
                        print("Error downloading '"+songName[i]+"', skipping.")
        else:
           if numberOfMissingSongs < 0:
               self.compareFiles(songLoc,songName)               
           else:
            print("No missing songs found, continuing.")
        print("\næøæøæøæøæøæøøææøøæøæ bund")
                
        
#######################################################################      
        
    #Functions to read songs and sound effects
    def readFolderPaths(self,loc,folderList):
      for i in range(len(folderList)):
          folder = folderList[i]
          folderList[i] = folder[0:-1]
      return folderList
        
    def readFileNames(self,loc,fileList):
        nameList = np.empty_like(fileList)
        for i in range(len(fileList)):
            file = fileList[i]
            file = os.path.basename(file)
            file = os.path.splitext(file)[0]
            nameList[i] = file
        return nameList
    
    def readEffectsInFolder(self,loc,normVol):
            fileList = glob.glob(loc+'\*.*')
            effectNames = self.readFileNames(loc,fileList)  
            
            soundClipArray = np.empty(len(fileList),dtype=object)
            for i in range(len(fileList)):
                soundClip = self.loadSoundClip(fileList[i],normVol)
                soundClipArray[i] = soundClip
            
            return effectNames, soundClipArray
              
    def readSoundEffects(self,loc,normVol):
        soundDict = {}
        
        folderList = glob.glob(loc+'\*\\')
        folderList = self.readFolderPaths(loc,folderList) 
        
        #Read files in the subfolders
        for i in folderList:
            names, readSounds = self.readEffectsInFolder(i,normVol)
            if len(readSounds) > 0:
                folderName = "DIR-" + os.path.basename(i)
                
                #Handle the pauses directories separately
                if folderName == "DIR-pauses-songnames":
                    songEffectsDict = {}
                    for k in range(len(names)):
                        songEffectsDict[names[k]] = readSounds[k]
                    soundDict[folderName] = songEffectsDict
                    
                elif folderName == "DIR-pauses-index":
                    songEffectsDict = {}
                    for k in range(len(names)):
                        songEffectsDict[names[k].split("_")[0]] = readSounds[k]
                    soundDict[folderName] = songEffectsDict
                    
                else:
                    soundDict[folderName] = readSounds
                    
        #Read files in the root loc
        names, readSounds = self.readEffectsInFolder(loc,normVol)
        for j in range(len(names)):
            soundDict[names[j]] = readSounds[j]
            
        return soundDict

#######################################################################
        
     #Normalise sound volume
    def normaliseVolume(self,sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)
    
    #Load soundclip and normalise
    def loadSoundClip(self,loc,normVol):
        soundClip = AudioSegment.from_file(loc).normalize()
        # soundClip = self.normaliseVolume(soundClip, normVol)
        return soundClip

    #Change speed of sound clips
    def speedChange(self,sound, speed=1.0):
        # Manually override the frame_rate. This tells the computer how many
        # samples to play per second
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
             "frame_rate": int(sound.frame_rate * speed)
          })
         # convert the sound with altered frame rate to a standard frame rate
         # so that regular playback programs will work right. They often only
         # know how to play audio at standard frame rate (like 44.1k)
        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
    
    #Function to make a random mashup of a given soundclip.
    def randomSoundMashup(self,clip,mean,speedLow,speedHigh,maxtime,seed):
        nSeed = self.randomInt(seed,size=2)
        number = self.pois(mean,nSeed[0])
        np.random.seed(nSeed[1])
        speeds = np.random.uniform(speedLow,speedHigh,number)
        
        hestetal = clip.duration_seconds
        loopnumber = np.int(np.ceil(maxtime/(speedLow*hestetal)))
        
        cliplist = np.empty(number,dtype=object)
        # Loop loopnumber of times
        for i in range(number):
            cliplist[i] = AudioSegment.empty()
    
            for j in range(loopnumber):
                cliplist[i] += clip
                
        # Change speeds
        for k in range(number):
            cliplist[k] = self.speedChange(cliplist[k],speeds[k])
            
        #overlay from the list of clips
        clipOut = cliplist[0]
        
        if number > 1:
            for i in range(1,number):
                clipOut = clipOut.overlay(cliplist[i],position=0)
                
        clipOut = clipOut[0:maxtime*1000]
        return clipOut,speeds,loopnumber
    
    
    
    #skal nok væk
    def randomBundClip(self,bundarray,seed=None):
        np.random.seed(seed)
        randomNumber = np.random.randint(0,len(bundarray))
        return bundarray[randomNumber]
    
    
    
    #Lower volume of a given AudioSegment in an interval
    def lowerVolumeInterval(self,clip,start,end,db):
        
        #Split clip in three parts to decrease volume in the middle
        song1 = clip[0:start]
        song2 = clip[start:end]
        song3 = clip[end:-1]
        
        #Lower volume
        song2 = song2 + db
        
        #Append songs
        song1 += song2
        song1 += song3
        return song1
    
    def addPauseBeforeSong(self,song,pause):
        songOut = AudioSegment.empty()
        songOut += pause
        songOut += song
        return songOut
    
    #Function to make a custom pause between songs using the songname.
    def customPause(self,index,songName,song):
        try:
            indexPauses = self.effects["DIR-pauses-index"]
        except:
            indexPauses = []
        try:
            customPauses = self.effects["DIR-pauses-songnames"]
        except:
            customPauses = []
        index = str(index)
        
        if index in indexPauses and songName in customPauses:
            out = self.fixPauseConflict(songName, index)
            if out == "II":
                songOut = self.addPauseBeforeSong(song,customPauses[songName])
                return songOut
            elif out == "IC":
                songOut = self.addPauseBeforeSong(song,indexPauses[index])
                return songOut
            
        elif index in indexPauses:
            songOut = self.addPauseBeforeSong(song,indexPauses[index])
            return songOut
        elif songName in customPauses:
            songOut = self.addPauseBeforeSong(song,customPauses[songName])
            return songOut
        else:
            return False
        
    #Help function to make random variables for the sound mashup function
    def randomSoundMashupRandomVariables(self,seed,meanMin=3,meanMax=11,timeMin=5,timeMax = 8):
        nSeed = self.randomInt(seed,size=2)
        mean = self.randomInt(nSeed[0],meanMin,meanMax,None)
        time = self.randomInt(nSeed[1],timeMin,timeMax,None)
        return mean, time
        
    #Help function to make a random sound sequence (qwabs)
    def randomPause(self,song,effect,seed,slow=0.2,fast=2,meanMin=3,meanMax=11,timeMin=5,timeMax=8):
        mean, time = self.randomSoundMashupRandomVariables(seed,meanMin,meanMax,timeMin,timeMax)
        qwabs, speeds,loopnumber = self.randomSoundMashup(effect,mean,slow,fast,time,seed)
        
        songOut = AudioSegment.empty()
        songOut += qwabs
        songOut += song
        
        return songOut,speeds,loopnumber

    #Function to count random events in order to seed properly
    def countRandomEvents(self):
        fuck = open(self.loc+"Klub100.py")
        lines = np.char.strip(np.squeeze(np.array([fuck.readlines()])))
        indBegin = np.where(lines == "#Begin randomness\n")[0][0]
        indEnd = np.where(lines == "#End randomness\n")[0][0]
        
        randomCounts = lines[indBegin+1:indEnd]
        i = 1
        for line in randomCounts:
            if "wtf" in line:
                i += 1
        
        randomList = [*range(1,i)]
        # randomList.pop(0)
        return randomList
    
    #Function to overlay a song with soundclip(s) 
    def overlaySound(self,song,clips,positions,db):
        if np.size(clips) != np.size(positions):
            raise Exception("Number of clips do not match number of positions")
        else:
            songOut = song
            if np.size(clips) > 1:
                for i in range(np.size(clips)):
                    songOut = songOut.overlay(clips[i]+db,position=positions[i])
            else:
                songOut = songOut.overlay(clips+db,position=positions)
            return songOut
        
    #Function to overlay the current song in the loop with a given song as read from the sound effects
    def overlaySoundSongname(self,currentSongName,song,overlaySongName,clips,positions,db):
        if overlaySongName != currentSongName:
            return False
        else:
            #Add a boolean to a dict that will hopefully be used in other features idk
            self.songOverlayBooleans[overlaySongName] = True
            return self.overlaySound(song,clips,positions,db)
            # return True
            
            
    # Function to add settings from a sound overlay    
    def addSoundOverlay(self,overlaySongName,clips,positions,db=10):
        settingsList = [overlaySongName,clips,positions,db]
        self.songOverlaySettings.append(settingsList)
        
    #Function to overlay a song with a mashed random soundclip at a random position
    def randomOverlaySound(self,song,clip,seed,slow=None,fast=2,pos=None,meanMin=3,meanMax=3,timeMin=1,timeMax=8):
        mean,time = self.randomSoundMashupRandomVariables(seed,meanMin,meanMax,timeMin,timeMax)
        slow = clip.duration_seconds/maxtime if slow is None else slow
        randomClip,speeds,loops = self.randomSoundMashup(clip,mean,slow,fast,time,seed)
        pos = self.randomInt(seed+1,minimum=0,maximum=(58-time)*1000,size=None) if pos is None else pos
        songOut = song.overlay(randomClip,position=pos)
        return songOut
    
    #Function to add clip before song and change the speed
    def soundClipSpeedChange(self,clip,song,speed):
        songOut = AudioSegment.empty()
        songOut += clip
        songChange = self.speedChange(song,speed)
        songOut += songChange
        return songOut
    
    def fixPauseConflict(self,songName,index):
        indexList = list(self.effects["DIR-pauses-index"].keys())
        indexList = list(map(int,indexList))
        lenCustoms = len(self.effects["DIR-pauses-songnames"])
        print("\nPause conflict:\nThere is a custom pause for the song '" + songName + "', but the current iteration also has an indexed pause.")
        remainingIndices = np.arange(int(index)+1,self.length)
        removeIndices = np.nonzero(np.isin(indexList,remainingIndices))
        randoms = np.delete(remainingIndices, removeIndices)
        
        print("\nYou can either ignore the custom pause ('IC'), ignore the indexed pause ('II'), move to a random new index ('RNI') or set a manual index ('SMI').")
        validCommands = ["IC","II","RNI","SMI"]
        
        while True:
            inString = input("Please enter a command:\n")
            if inString not in validCommands:
                print("\nInvalid command.\nPlease input either 'IC' to ignore the custom pause, 'II' to ignore the indexed pause, 'RNI' to move to a random new index or 'SMI' to set a manual index.")
            elif inString == "IC":
                print("Ignoring the custom pause for '"+ songName +"'.\n")
                return 'IC'
            elif inString == "II":
                print("Ignoring the indexed pause for index "+ index +".\n")
                return 'II'
            elif inString == "RNI":
                print("Assigning the indexed pause with a random new index.\n")
                if len(randoms) > 0:
                    newIndex = np.random.choice(randoms,replace=False)
                    print(newIndex)
                    self.effects["DIR-pauses-index"][str(newIndex)] = self.effects["DIR-pauses-index"][str(index)]
                    del self.effects["DIR-pauses-index"][str(index)]
                    return 'II'
                else:
                    print("No more locations available. Please ignore either the custom or the indexed pause.")
            elif inString == "SMI":
                print("Manually setting a new index.\n")
                
                if len(randoms) == 0:
                    print("No more locations available. Please ignore either the custom or the indexed pause.")
                else:
                    print("Please enter a new index from the below list. If you wish to use another command, type 'UP'.\n")
                    print(np.sort(randoms))
                    while True:
                        newIndex = input()
                        if newIndex == "UP":
                            break
                        else:
                            try:
                                newIndex = int(newIndex)
                                if newIndex not in randoms:
                                    print("Please pick an index from the list given above.")
                                    continue
                                else:
                                    self.effects["DIR-pauses-index"][str(newIndex)] = self.effects["DIR-pauses-index"][str(index)]
                                    del self.effects["DIR-pauses-index"][str(index)]
                                    return 'II'
                            except:
                                print("Error - please enter an integer.")
                                continue
            
    
    #hest
    def generateKlub100(self,url,songName,randomBool,seed):
        songsList = self.initSongs(randomBool,songName,seed,self.songs,self.positions)
        
        BumsernesKlub100 = AudioSegment.empty()
        BumsernesKlub100 += self.effects["intro"]
        
        print("\nNow stitching the songs...")
        
        #Loop begin
        i = 0
        songcounter = 1
        while songcounter <= self.length:
            print('Qwabs100 is at song',songcounter,'out of '+str(self.length))
            name = songName[songsList[i]]
            song = self.loadSoundClip(self.loc + "songs\\" + name + ".mp4", self.normVol)
            # Adds fade in and fade out to the song
            song = song.fade_in(2000).fade_out(2000)
            
            #Add any potential song overlays
            for k in self.songOverlaySettings:
                overlayedSong = self.overlaySoundSongname(name,song,*k)
                if overlayedSong != False:
                    song = overlayedSong

            #Add either a custom pause or Qwabs
            customPause = self.customPause(i,name,song)
            if customPause != False:
                song = customPause
            elif i > 0:
                song,_,_ = self.randomPause(song,self.effects["kwabs"],seed)                

            i += 1
            songcounter += 1
            BumsernesKlub100 += song
        #Loop end
        
        # Adds the outro file to the output file
        BumsernesKlub100 += self.effects["outro"]
        print("\nDone sticthing. Now exporting the file - this might take some time.\n")

        # Exports the output file
        BumsernesKlub100.export(loc + 'BumsernesKlub100_seed{}'.format(self.seed) + '.mp4',format="mp4")
        print('Seed used was {}'.format(self.seed))
        print('bonsjuar madame')
        
    #Help function to find the indices for a list of songs in a larger list of songs
    def findIndices(self,songList,songs):
        songIndices = []
        for i in range(len(songs)):
            try:
                ind = songList.tolist().index(songs[i])
                songIndices.append(ind)
            except:
                print("Song '" + songs[i] + "' does not exist. Ignoring.")
        songIndices = np.array(songIndices)
        return songIndices

    
    #Initialise the song list randomly or sequentially. If random, it is possible to force certain songs by names to appear in the list.
    def initSongs(self,randomBoolean,songNames,seed,songs=[],positions=[]):
        if not randomBoolean:
            if len(songs) > 0:
                print("Forced songs ignored.\n")
                print("You attempted to force songs, but the songs are loaded sequentially and are not randomized. If you wish to include the songs, please put the songs in the respective order in the relevant spreadsheet.")
        
            songsInKlub100 = np.arange(len(self.url))
        # If the songlist is random...
        else:
            positions = np.array(positions)
            songsInKlub100 = np.random.choice(len(self.url),len(self.url),replace=False)

            #If we are attempting to force songs...
            if len(songs) > 0:
                lengthDif = self.length-len(songs)

                if len(songs) < len(positions):
                    print("Error: length of array of positions is longer than the number of forced songs. The two arrays must be the same length.\nIgnoring forced songs.")
                elif len(songs) > len(positions) and len(positions) != 0:
                    print("Error: length of array of songnames is longer than the length of positions. If you wish to have only some of the forced songs be in a specific position, please denote the position of the randomly placed songs as 'None'. The two arrays must be the same length.\nIgnoring forced songs.")
                elif lengthDif < 0:
                    print("Error: you are trying to force a larger number of songs than the length of the Klub100. Ignoring forced songs.")
                elif len(positions) != 0 and max(positions[positions!=None]) > self.length - 1:
                    print("Error: you are attempting to position a forced song at an index larger than what is available given by the length-parameter. Ignoring forced songs.")
                else:
                    # If no errors. This code is rather confusing and I do not understand it anymore :)

                    #Find the indices of the songs from the songNames array as read in the init
                    songIndices = self.findIndices(songNames,songs)
                    
                    #The relevant indices of the song indices in the random array generated by np.random.choice
                    listIndices = np.nonzero(np.isin(songsInKlub100,songIndices))
                    
                    #The reduced output array 
                    reducedSongsInKlub100 = np.delete(songsInKlub100,listIndices)
   
                    #Two subsets of the reduced output array. This is to stitch them later, taking into account e.g. mashups of songs
                    reducedList1 = reducedSongsInKlub100[0:lengthDif].tolist()
                    reducedList2 = reducedSongsInKlub100[lengthDif+1:-1].tolist()
                    
                    #List and dictionary for the random forced / positionally forced songs
                    randomForcedSongsList = []
                    positionedForcedSongsList = {}
                    
                    for j in range(len(songIndices)):
                        #If there are positions...
                        if len(positions) > 0:
                            #If a "None" position, add the index to the list
                            if positions[j] == None:
                                randomForcedSongsList.append(songIndices[j])
                            #Else add the song index as a value in a dictionary with keys the positions
                            else:
                                positionedForcedSongsList[positions[j]] = songIndices[j]                
                        
                        #If no positions given, all songs are random
                        else:
                            randomForcedSongsList.append(songIndices[j])
                            
                    #Add the randomly forced songs back to the reduced random subset
                    reducedList1.extend(randomForcedSongsList)
                    
                    #Scramble the combined list
                    np.random.seed(seed)
                    reducedList1 = np.random.choice(reducedList1,len(reducedList1),replace=False)
                    
                    #Ensuring that the positioned forced songs are added at the correct indices.
                    songKeys = list(positionedForcedSongsList.keys())
                    songKeysToAdd = songKeys - np.arange(len(songKeys))
                    songValues = list(positionedForcedSongsList.values())
                    
                    #Add the positioned songs to the first subset
                    if len(songKeysToAdd) > 0:
                        reducedList1 = np.insert(reducedList1,songKeysToAdd,songValues)
                    
                    #Adding the two reduced lists back together to accommodate the cases where more than self.length songs have been used (i.e. with mashups)
                    songsInKlub100 = np.concatenate((reducedList1,reducedList2))

        return songsInKlub100
    
    def addForcedSongs(self,songs,positions=[]):
        print("\nForcing songs \n" + str(songs))
        if len(positions) == 0:
            print("... at random positions.")
        else:
            print("... at the index locations: \n"+str(positions)+". \n'None' is random.")
        self.songs = songs
        self.positions = positions
                      
            

# der skal tilføjes funktionalitet til at:
    
# man skal kunne tvinge givne sange til at være med hvis der trækkes tilfældige sange fra listen
#TJEK
    
# mappe med pauser i rækkefølge "1_hest.m4a" som indlæses på det respektive index
    # hvis overlap med pauses skal der ske noget (input prompt, pauses trumfer eller andet)
#TJEK
    #man skal måske kunne vælge en standardindstilling?


#funktionalitet til at tilføje tilfældige pauser fra en eller flere mapper
    # hvordan skal det fungere hvis der tilføjes tilfældige pauser
    #

#seeds skal virke igen

#der skal kunne tilføjes overlays hvis givne conditions opfyldes
    #ex: et random overlay, der har en qwabs mellem 0.2 og 2 hastighed: der afspilles et bundklip hvis minimumhastigheden af overlays er under 0.3
        
#chance for at tilfældige sange mashes
#chance for at en given sang ændres til dobbelt eller halv hastighed 
    
    
# Reading sound files
normVol = -20
loc = "C:\\Users\\Marcus\\Desktop\\k100\\Klub100\\"
length = 5
test = Klub100(loc,normVol,length,localBool=True)
# test.addSoundOverlay('helmig', test.effects["DIR-pat"], [30500,36500,42500,48000,53500])
test.addForcedSongs(["helmig"],[4])
test.generateKlub100(test.url, test.songName, True,test.seed)
       

        


#%%
count1 = 0
count2 = 0
for k in range(100):
    joke = test.initSongs(True,songName,["helmig","the sign","model"],[0,3,None])[0:length]
    index = np.where(joke==132)[0][0]
    if index == 1:
        count1 += 1
    elif index == 2:
        count2 += 1
    else:
        print("fuck")
        break
print(count1)
print(count2)    
    
# print(np.where(joke==107))

# hest = np.where(joke[0:length]==107)[0]

print(joke[0:length])
            
# print(test.initSongs(True,songName,["helmig"])[0:length])


# test.generateKlub100(test.url, test.songName, test.seed)
 

#%% Alt under dette er gammel kode der skal skrives om
# 


#%%
# Defines the output file
BumsernesKlub100 = AudioSegment.empty()
BumsernesKlub100 += intro


#%%
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

