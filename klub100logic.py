import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
os.chdir(file_dir)

import pytube
import pandas as pd
from pydub import AudioSegment
import numpy as np
import random
import glob
import klub100sheets as sheets
import urllib.request
from gtts import gTTS as gt
import uuid
import subprocess


#Klub100 class 
class Klub100(object):
    
    def __init__(self,loc,length=100,seed=None,filename = "k100.xlsx",localBool=False,indexedShoutoutBool=False,prefix='',lan='da'):
        """
        Initialise the klub100 object.

        Parameters
        ----------
        loc : string.
            File path to the folder where the output file will be generated and all songs downloaded to.
        length : int, optional
            Length of the Klub100. The default is 100.
        seed : int, optional
            Seed to be used by the random calls. The default is None.
        filename: string, optional
            Name of the local .xlsx-file from which songs are taken.
        localBool : boolean, optional
            Boolean to determine whether to use Google Sheets or the local excel file. The default is False.
        indexedShoutoutBool : boolean, optional
            Boolean to determine whether any downloaded shoutouts in the shoutouts-folder as indexed pauses. The default is False.
        prefix : string or list, optional
            Prefix for the shoutouts. The default is ''.
        lan : string or list, optional
            Language for the shoutouts. The default is 'da'.
        """
        print("Initialising Klub100 of length " + str(length) + ".\n")
        
        #Initialise parameters
        #Root folder location
        self.loc = loc
        
        #Should we use the shoutouts as indexed pauses?
        self.indexedShoutoutBool = indexedShoutoutBool
        
        if self.indexedShoutoutBool:
            self.indexedPauseDir = "DIR-shoutout"
        else:
            self.indexedPauseDir = "DIR-pauses-index"
            
        #Random mash songs settings
        self.randomMashAddedBoolean = False
                
        #Forced song arrays
        self.songs = []
        self.positions = []
        
        #Length of klub100 :)
        self.length = length
        self.seed = random.randrange(100000) if seed is None else seed
        random.seed(self.seed)
        
        #Arrays to hold settings for custom effects
        self.songOverlaySettings = []
        
        #Dictionary to hold info about pauses
        self.pauseDict = {}
        self.pauseCounterDict = {}
        
        #More dictionaries :)
        self.limitedPauseDictCount = {}
        
        #Dictionaries to hold information about conditional effects
        self.conditionsDict = {}
        self.statusDict = {}
        
        #Settings for random pauses
        self.totalWeights = 0
        self.randomPauses = []
    
        #Read and download songs locally or from Sheets
        url, startSec, songName, shoutouts = self.readSongsAndShoutouts(loc,localBool,filename)
        self.downloadSongs(loc,url,startSec,songName)
        self.downloadShoutouts(shoutouts,prefix,lan)
        
        self.url = url
        self.startSec = startSec
        self.songName = songName
        
        eLoc = loc + "effects\\"
        print("\nReading sound effects from directory\n" + eLoc)
        self.effects = self.readSoundEffects(loc + "effects\\")
        print("Finished reading sound effects.")
        
         
        
    def randomInt(self,minimum=0,maximum=99999999,size=20000):
        if size == None:
            return random.randint(minimum,maximum)
        else:
            return [random.randint(minimum,maximum) for x in range(size)]
    
    def randomFloat(self,size=None):
        if size == None:
            return random.uniform(0,1)
        else:
            return [random.uniform(0,1) for x in range(size)]

    
    def findNearestGreaterThan(self,searchVal, inputData):
        diff = inputData - searchVal
        diff[diff<0] = np.inf
        idx = diff.argmin()
        return idx
    
    #Zero-truncated poisson distribution
    def pois(self,mean,seed):
        out = 0
        while out < 1:
            np.random.seed(seed)
            out = np.random.poisson(mean)
            
            if type(seed) == int and out == 0:
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
    def readSongsAndShoutouts(self,loc,localBool,filename):
        
        if localBool == False:
            if self.connect():
                print("Gathering songs (and potential shoutouts) from Google Sheets.")
                data = sheets.klubhest(loc)
            else: 
                print("Attempted to gather songs from Google Sheets, but you are not connected to the internet. Gathering from local file instead.")
                print(loc + filename)
                # Reads data in excel file 
                data = pd.read_excel(loc + filename)
        else:
            print("Gathering songs (and potential shoutouts) from local Excel file.")
            print(loc + filename)
            # Reads data in excel file 
            data = pd.read_excel(loc + filename)
            

        
        url = data.loc[:,'Link']
        songName = data.loc[:,'Sang']
        nullIndex = np.where(pd.isnull(data.loc[:,'Starttid i sang [s]']))[0]
        if len(nullIndex) > 0:
            data.loc[:,'Starttid i sang [s]'][nullIndex] = 0
        startSec = data.loc[:,'Starttid i sang [s]'].astype('int')
        shoutouts = data.loc[:,'Shoutouts'].dropna()
            
        return url, startSec, songName, shoutouts


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
                    print("'" +file+".mp4'" + " is available locally but not in the used sheet.")
                   

       

    #Download songs using Google Sheets API (if internet) or using a local Excel
    def downloadSongs(self,loc,url,startSec,songName):
        
        #Define the song location
        songLoc = loc + "songs\\"
        
        #dict.fromkeys to remove duplicate values
        numberOfSongs = len(dict.fromkeys(url))
        numberOfMissingSongs = numberOfSongs-len(glob.glob(songLoc+'*.*'))

        if numberOfMissingSongs > 0:
            print("Downloading {} missing song(s) out of {}".format(numberOfMissingSongs,numberOfSongs) + " in total.")
            for i in range(len(url)):
                # Renames the song
                filename = songLoc + songName[i]
                if os.path.isfile(filename + ".mp4") == False:
                    print("Downloading song " + songName[i] + ", {}".format(i+1)+" out of "+str(len(url)))
                    try:     
                    #For some reason, youtube-dl is atm very slow compared to pytube.
                    #Using pytube for youtube downloads, and youtube-dl for anything else.
                        if url[i].find("youtube") == -1:
                            process = subprocess.Popen(['youtube-dl',
                                    '--extract-audio',
                                    '--audio-format', 'm4a',
                                    '--audio-quality','0',
                                    '-o', filename + ".m4a", url[i]],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                            _, err = process.communicate()
                            # print(err)
                            os.rename(filename + ".m4a",songLoc + songName[i] + '.mp4')
               
                        else:
                            youtube = pytube.YouTube(url.loc[i])
                            song = youtube.streams.get_audio_only()
                            out = song.download(songLoc)
                            os.rename(out,songLoc + songName[i] + '.mp4')
                                
                        #Only save the minute needed for the final klub100
                        song = self.loadSoundClip(songLoc+songName[i]+'.mp4')
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


    # def downloadShoutouts(self,shoutouts):
    #     for k in shoutouts
        
                
        
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
    
    def readEffectsInFolder(self,loc):
            fileList = glob.glob(loc+'\*.*')
            effectNames = self.readFileNames(loc,fileList)  
            
            soundClipArray = np.empty(len(fileList),dtype=object)
            for i in range(len(fileList)):
                soundClip = self.loadSoundClip(fileList[i])
                soundClipArray[i] = soundClip
            
            return effectNames, soundClipArray
              
    def readSoundEffects(self,loc):
        soundDict = {}
        
        folderList = glob.glob(loc+'\*\\')
        folderList = self.readFolderPaths(loc,folderList) 
        
        #Read files in the subfolders
        for i in folderList:
            names, readSounds = self.readEffectsInFolder(i)
            if len(readSounds) > 0:
                folderName = "DIR-" + os.path.basename(i)
                
                #Handle the pauses directories separately
                if folderName == "DIR-pauses-songnames":
                    songEffectsDict = {}
                    for k in range(len(names)):
                        songEffectsDict[names[k]] = readSounds[k]
                    soundDict[folderName] = songEffectsDict
                    
                elif folderName == self.indexedPauseDir:
                    songEffectsDict = {}
                    for k in range(len(names)):
                        songEffectsDict[names[k].split("_")[0]] = readSounds[k]
                    soundDict[folderName] = songEffectsDict
                    
                else:
                    soundDict[folderName] = readSounds
                    
        #Read files in the root loc
        names, readSounds = self.readEffectsInFolder(loc)
        for j in range(len(names)):
            soundDict[names[j]] = readSounds[j]
            
        return soundDict

#######################################################################
        

    #Load soundclip and normalise
    def loadSoundClip(self,loc):
        soundClip = AudioSegment.from_file(loc).normalize()
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
    def randomSoundMashup(self,clip,mean,speedLow,speedHigh,maxtime):
       
        seed = random.randrange(100000)
        number = self.pois(mean,seed)
        
        speeds = [random.uniform(speedLow,speedHigh) for x in range(number)]
       
        hestetal = clip.duration_seconds
        loopnumber = np.int(np.ceil(maxtime/(min(speeds)*hestetal)))
        cliplist = np.empty(number,dtype=object)
        numOfEffects = sum(([maxtime/hestetal*x for x in speeds]))
        
        

        
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
        return clipOut,speeds,numOfEffects
    
    def randomSoundEffect(self,effectDirName):
        effectDir = self.effects[effectDirName]
        randomNumber = random.randrange(0,len(effectDir))
        return effectDir[randomNumber]
    

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
            if self.indexedShoutoutBool:
                indexPauses = self.effects["DIR-shoutout"]
            else:
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
    def randomSoundMashupRandomVariables(self,meanMin=3,meanMax=11,timeMin=5,timeMax = 8):
        mean = self.randomInt(meanMin,meanMax,None)
        time = self.randomInt(timeMin,timeMax,None)
        return mean, time
        
    #Help function to make a random sound sequence (qwabs)
    def randomPause(self,song,effect,slow=0.2,fast=2,meanMin=3,meanMax=11,timeMin=5,timeMax=8):
        mean, time = self.randomSoundMashupRandomVariables(meanMin,meanMax,timeMin,timeMax)
        qwabs, speeds,numOfEffects = self.randomSoundMashup(effect,mean,slow,fast,time)
        songOut = self.addPauseBeforeSong(song,qwabs)        
        return songOut,speeds,numOfEffects,slow,fast,meanMin,meanMax,mean,timeMin,timeMax,time
    
    #Function to overlay a song with soundclip(s) 
    def overlaySound(self,song,clips,pos,db):
        # print(type(clips))
        if not isinstance(clips,np.ndarray):
            clips = [clips]

        # print(clips)
        # print(pos)
            
        if len(clips) != np.size(pos):
            raise Exception("Number of clips do not match number of positions")
        else:
            songOut = song
            if len(clips) > 1:
                for i in range(np.size(clips)):
                    time = clips[i].duration_seconds
                    songOut = self.lowerVolumeInterval(songOut, pos[i], time*1000+pos[i], db)
                    songOut = songOut.overlay(clips[i],position=pos[i])
            else:
                time = clips[0].duration_seconds
                songOut = self.lowerVolumeInterval(songOut, pos, time*1000+pos, db)
                songOut = songOut.overlay(clips[0],position=pos)
                
            return [songOut,["positions"],[pos]]

        
    # #Function to overlay the current song in the loop with a given song as read from the sound effects
    # def overlaySoundSongname(self,currentSongName,song,overlaySongName,clips,positions,db):
    #     if overlaySongName != currentSongName:
    #         return False
    #     else:
    #         #Add a boolean to a dict that will hopefully be used in other features idk
    #         self.songOverlayBooleans[overlaySongName] = True
    #         return self.overlaySound(song,clips,positions,db)
    #         # return True
            
    #Function to add clip before song and change the speed
    def soundClipSpeedChange(self,clip,song,speed):
        songOut = AudioSegment.empty()
        songOut += clip
        songChange = self.speedChange(song,speed)
        songOut += songChange
        return songOut
    
    def fixPauseConflict(self,songName,index):
        
        validCommands = ["IC","II","RNI","SMI"]
        indexList = list(self.effects["DIR-pauses-index"].keys())
        indexList = list(map(int,indexList))
        print("\nPause conflict:\nThere is a custom pause for the song '" + songName + "', but the current iteration also has an indexed pause.")
        
        if self.standardPauseConflictSetting is not None:
            if self.standardPauseConflictSetting not in ["IC","II"]:
                print("\nError: the standard setting for the pause conflict can only be to either ignore the indexed pause ('II') or to ignore the custom pause. Defaulting to ignore the indexed pause.\n")
                return "II"
            else:
                print("Using the standard setting of '"+ self.standardPauseConflictSetting+"'.\n")
                return self.standardPauseConflictSetting
        else:
    
            remainingIndices = np.arange(int(index)+1,self.length)
            removeIndices = np.nonzero(np.isin(indexList,remainingIndices))
            randoms = np.delete(remainingIndices, removeIndices)
            print("\nYou can either ignore the custom pause ('IC'), ignore the indexed pause ('II'), move to a random new index ('RNI') or set a manual index ('SMI').")
            
            
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
    def initSongs(self,randomBoolean,songNames,songs=[],positions=[]):
        if not randomBoolean:
            if len(songs) > 0:
                print("Forced songs ignored.\n")
                print("You attempted to force songs, but the songs are loaded sequentially and are not randomized. If you wish to include the songs, please put the songs in the respective order in the relevant spreadsheet.")
        
            songsInKlub100 = np.arange(len(self.url))
        # If the songlist is random...
        else:
            positions = np.array(positions)
            ln = len(self.url)
            songsInKlub100 = random.sample(range(ln),k=ln)
            # songsInKlub100 = np.random.choice(len(self.url),len(self.url),replace=False)

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
                    # If no errors. This code is a bit confusing and I do not really understand it anymore :)

                    #Find the indices of the songs from the songNames array as read in the init
                    songIndices = self.findIndices(songNames,songs)
                    
                    #The relevant indices of the song indices in the random array generated by np.random.choice
                    listIndices = np.nonzero(np.isin(songsInKlub100,songIndices))
                    
                    #The reduced output array 
                    reducedSongsInKlub100 = np.delete(songsInKlub100,listIndices)
   
                    #Two subsets of the reduced output array. This is to stitch them later, taking into account e.g. mashups of songs
                    reducedList1 = reducedSongsInKlub100[0:lengthDif+1].tolist()
                    reducedList2 = reducedSongsInKlub100[lengthDif+1:].tolist()
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
                    reducedList1 = random.sample(reducedList1,len(reducedList1))
                    
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
                      
    
               
    def addRandomMashedPause(self,weight,effectName,slow=0.2,fast=2,meanMin=3,meanMax=11,timeMin=5,timeMax=8):
        eff = self.effects[effectName]
        mashBool = True
        self.totalWeights += weight
        settingsList = [mashBool,weight,effectName,eff,slow,fast,meanMin,meanMax,timeMin,timeMax]
        self.randomPauses.append(settingsList)
        
    def addRandomPause(self,weight,effectName):
        
        eff = self.effects[effectName]
        mashBool = False
        self.totalWeights += weight
        settingsList = [mashBool,weight,effectName,eff]
        self.randomPauses.append(settingsList)
        
    def addLimitedPause(self,weight,effectName):
        eff = self.effects[effectName]
        mashBool = False
        self.totalWeights += weight
        
        if len(eff) > 0:
            effLength = len(eff)
        else:
            effLength = 1
        
        ID = uuid.uuid1()
        self.limitedPauseDictCount[ID] = weight/effLength
        settingsList = [mashBool,weight,effectName,eff,ID]
        self.randomPauses.append(settingsList)
        

        #not really random lmao
    def chooseRandomPause(self):
        randomNumber = self.randomFloat()
        probsPauses = []
        for count,i in enumerate(self.randomPauses):
            probsPauses.append(i[1]/self.totalWeights)

        propsPauses = np.cumsum(probsPauses)

        
        idx = self.findNearestGreaterThan(randomNumber,propsPauses)
        # print(self.randomPauses[idx][2])
        return self.randomPauses[idx][0],self.randomPauses[idx],idx
    
    
    def insertRandomPause(self,song):
        if len(self.randomPauses) == 0:
            return [False]
        
        
        while True:
            mashBool,settings,idx = self.chooseRandomPause()
            
            #Check if there are no more effects left to be used in a limited pause
            if isinstance(settings[4],uuid.UUID) and len(self.randomPauses[idx][3]) == 0:
                self.randomPauses = np.delete(self.randomPauses,idx,0)
                continue
            
            break

        if settings[2] not in self.pauseCounterDict:
            self.pauseCounterDict[settings[2]] = 1
        else:
            self.pauseCounterDict[settings[2]] += 1
            
        if mashBool:
            return True,self.randomPause(song,*settings[3:]),settings[2]
        else:
            eLen = len(settings[3])
            # print("length of effect folder:" + str(eLen))
             
            if eLen > 0:
                effectIdx = self.randomInt(0,eLen-1,None)
                effect = settings[3][effectIdx]
                
                #If the fourth element of the settings is a unique ID
                if isinstance(settings[4],uuid.UUID):
                    self.randomPauses[idx][3] = np.delete(self.randomPauses[idx][3],effectIdx)
                    
            else:
                effect = settings[3]

            effectTime = effect.duration_seconds
            return True,(self.addPauseBeforeSong(song,effect),1,1,1,1,1,1,1,effectTime,effectTime,effectTime),settings[2]
        
        
    def helpShoutoutDownloads(self,shoutoutLoc,shoutout,index,prefix,lan,shoutoutLength):
        if os.path.isfile(shoutoutLoc + str(index) + "_" +prefix + shoutout + "_" + lan +".mp3") == False:
            print("Downloading shoutout '" + shoutout + "', {}".format(index+1)+" out of "+str(shoutoutLength))
            # try:
            sound = gt(prefix + " " + shoutout,lang=lan)
            sound.save("effects\\shoutout\\" + str(index) +"_"+ prefix + shoutout + "_" + lan +".mp3") 
            return True
        else:
            return False
  

    def downloadShoutouts(self,shoutouts,prefix,lan):
        shoutoutLoc = self.loc + "effects\\shoutout\\"
        print("\nDownloading any missing shoutouts from Google Translate.")
        
        if type(prefix) is not str:
            if len(prefix) == 1:
                prefix = prefix[0]
            else:
                try: 
                    if len(prefix) != len(shoutouts):
                        print("Error: the length of the prefix-list is not the same as the length of the shoutouts. Using the first entry in the list.")
                        prefix = prefix[0]
                except:
                    print("Error: if you wish to use multiple prefixes, please ensure that the input is given in a list-type.")
        
        
        if type(lan) is not str:
            if len(lan) == 1:
                lan = lan[0]
            else:
                try: 
                    if len(prefix) != len(shoutouts):
                        print("The length of the language-list is not the same as the length of the shoutouts. Using the first entry in the list.")
                        lan = lan[0]
                except:
                    print("If you wish to use multiple prefixes, please ensure that the input is given in a list-type.")
        
        
        if type(prefix) == str:
            prefix = np.repeat(prefix,len(shoutouts))
            
        if type(lan) == str:
            lan = np.repeat(lan,len(shoutouts))
            
        
        shoutoutLength = len(shoutouts)
        downloadedBool = []
        for k in range(shoutoutLength):
            downloadedBool.append(self.helpShoutoutDownloads(shoutoutLoc,shoutouts[k],k,prefix[k],lan[k],shoutoutLength))
       
        if not any(downloadedBool):
            print("No missing shoutouts. Continuing.")
        
        if self.indexedShoutoutBool:
            string = "The shoutouts are used as indexed pauses. This means that any indexed pauses in the directory 'pauses-index' will not be used. If you wish to use a combination of the two, please disable the 'indexedShoutoutBool'-boolean and move the respective files between the relevant folders."
        else:
            string = "The shoutouts are not used as indexed pauses and will only be enabled if you add the folder as a random pause. If you wish to use the shoutouts as indexed pauses, please enable the 'indexedShoutoutBool'-boolean."
        print("Finished!\n\n" + string)
        
        
              
    def randomSpeedChange(self,song,chance,speed,effect=None):
        randomNum = self.randomFloat()
        
        if randomNum < chance:
            songOut = AudioSegment.empty()
            if effect is not None:
                songOut += effect
                
            speedChangedSong = self.speedChange(song,speed)
            songOut += speedChangedSong
            return [songOut,["randomNum"],[randomNum]]
        else:
            return [song,["randomNum"],[randomNum]]

    def randomMashup(self,chance,currentSong,nextSongName,effect=None):
        randomNum = self.randomFloat()
        
        if randomNum < chance:
            initTime = 0
            
            mashedSong = AudioSegment.empty()
            if effect is not None:
                mashedSong += effect
                initTime = effect.duration_seconds
                
            nextSong = self.loadSoundClip(self.loc + "songs\\" + nextSongName + ".mp4")
            mashedSong += currentSong.overlay(nextSong,position=initTime*1000)  
            return mashedSong
        else:
            return currentSong
               

        
#Alt under dette virker (formodentlig), men det er et kæmpe clusterfuck og bør renskrives og streamlines :)

    def depthCount(self,x):
       return int(isinstance(x, list)) and len(x) and 1 + max(map(self.depthCount, x))
    
    #Add condition to a given random sound effect.
    def addCondition(self,ID,conditions):
        callableList = [f for f in conditions if isinstance(f,list)]


        if len(callableList) == 0:
            callableSettings = conditions[1:]
            conditions = conditions[0]
            
        elif self.depthCount(callableList) == 2:
            conditions = []
            callableSettings = []
            #Split the list in the conditional callables and their settings to be run in the loop
            for j in callableList:
                conditions.append(j[0])
                callableSettings.append(j[1:])
                
                
        elif self.depthCount(callableList) == 3:
            conditions = [[] for x in range(len(callableList))]
            callableSettings = [[] for x in range(len(callableList))]
            
            # print(callableList)
            for orCount,orSettings in enumerate(callableList):
                if not(self.depthCount(orSettings) == 2):
                        orSettings = [orSettings]
                        
                # print(orSettings)
                for sets in orSettings:
      
                    conditions[orCount].append(sets[0])
                    callableSettings[orCount].append(sets[1:])
            
        if ID in self.conditionsDict:
            self.conditionsDict[ID][0] = conditions
            self.conditionsDict[ID][1] = callableSettings
        else:
            self.conditionsDict[ID] = [conditions,callableSettings]
            
    def addRandomMash(self,chance,effect=None):
        self.randomMashAddedBoolean = True
        self.mashSettings = [chance,effect]
   
        
    def addRandomSpeedChange(self,chance,speed,effectName = None, ID = None):
        if ID is None:
            ID = uuid.uuid1()
        conditions = []
        
        effect = None if effectName is None else self.effects[effectName]

        settings = [chance,speed,effect]
        if ID not in self.conditionsDict:
            self.conditionsDict[ID] = [conditions,[],settings,self.randomSpeedChange]
        else:
            self.conditionsDict[ID].extend([settings,self.randomSpeedChange])
            
    #Function to overlay a song with a mashed random soundclip at a random position
    def randomOverlaySound(self,song,mashBool,db,chance,effect,slow,fast,pos,meanMin,meanMax,timeMin,timeMax):
        if isinstance(effect,np.ndarray):
            effect = self.randomSoundEffect(effect)
        
        randomNum = self.randomFloat()
        if randomNum < chance:
            if mashBool:
                mean,time = self.randomSoundMashupRandomVariables(meanMin,meanMax,timeMin,timeMax)
                slow = effect.duration_seconds/time if slow is None else slow
                randomClip,speeds,numOfEffects = self.randomSoundMashup(effect,mean,slow,fast,time)
            else:
                randomClip = effect
                speeds = 1
                numOfEffects = 1
                time = effect.duration_seconds
                
            pos = self.randomInt(minimum=0,maximum=int((58-time)*1000),size=None) if pos is None else pos
            songOut = self.lowerVolumeInterval(song, pos, time*1000+pos, db)
            songOut = songOut.overlay(randomClip,position=pos)
            
            return [songOut,["randomNum","speeds","numOfEffects","positions"],[randomNum,speeds,numOfEffects,pos]]
        else:
            # speeds = 1
            # numOfEffects = 1
            # pos = 0
            return [song,False]
    
    def addRandomOverlaySound(self,chance,effectName,mashBool=False,db=-15,ID=None,slow=None,fast=2,pos=None,meanMin=3,meanMax=4,timeMin=5,timeMax=8):
        if ID is None:
            ID = uuid.uuid1()
        conditions = []
        effect = self.effects[effectName]

        settings = [mashBool,db,chance,effect,slow,fast,pos,meanMin,meanMax,timeMin,timeMax]
        if ID not in self.conditionsDict:
            self.conditionsDict[ID] = [conditions,[],settings,self.randomOverlaySound]
        else:
            self.conditionsDict[ID].extend([settings,self.randomOverlaySound])
                 
    #     # Function to add settings from a sound overlay    
    # def addSoundOverlay(self,overlaySongName,effectName,positions,db=10):
    #     clips = self.effects[effectName]
    #     pos = [i*1000 for i in positions]
    #     settingsList = [overlaySongName,clips,pos,db]
    #     self.songOverlaySettings.append(settingsList)
             
        # Function to add settings from a sound overlay    
    def addSoundOverlay(self,effectName,positions,db=-15,ID = None):
        if ID is None:
            ID = uuid.uuid1()
        conditions = []
        
        if isinstance(effectName,list):
            effect = effectName
            pos = positions
        else:
            effect = self.effects[effectName]
            if isinstance(positions,int):
                pos = positions
            else:
                pos = [i*1000 for i in positions]

        
        settings = [effect,pos,db]

        if ID not in self.conditionsDict:
            self.conditionsDict[ID] = [conditions,[],settings,self.overlaySound]
        else:
            self.conditionsDict[ID].extend([settings,self.overlaySound])
############################################################################################
# Functions used to add conditionals to random effects

    
    def lookupSongNameByRelativeIndex(self,name,index):
        # print(self.i)
        # print(index)
        try:
            if self.songName[self.songsList[self.i+index]] in name:
                return True
            return False
        except:
            return False
    
    #Used to add conditionals to random effects    
    def lookupCurrentSongName(self,name):
        return self.lookupSongNameByRelativeIndex(name,0)
    
    

    #Used to add conditionals to random effects  
    def lookupCurrentIndex(self,index):
        if self.i in index:
            return True
        return False
    
    #should probably make this an eval :)
    def helpCompareLookups(self,compareStr,lookup,value):
        if compareStr == ">":
            if lookup > value:
                return True
            return False
            
        elif compareStr == "<":
            if lookup < value:
                return True
            return False
            
        elif compareStr == "=":
            if lookup == value:
                return True
            
        else:
            print("\nError: you have used an invalid comparison string. Please use either '>','<' or '='.")
            return False
        
    def helpdictIndex(self,length,compareIndex):
        return (length - 1 - compareIndex)%length
    
    def lookupSpeed(self,ID,compareStr,speed,relativeCompareIndex = 0,func="min"):
        try:                
            dictIndex = self.helpdictIndex(len(self.statusDict[ID]),relativeCompareIndex)
            dictSpeed = eval(func)(self.statusDict[ID][dictIndex]["speeds"])
            return self.helpCompareLookups(compareStr,dictSpeed,speed)
        except: 
            return False
        
    def lookupNumOfEffects(self,ID,compareStr,num,relativeCompareIndex = 0):
        try:
            dictIndex = self.helpdictIndex(len(self.statusDict[ID]),relativeCompareIndex)
            numOfEffects = self.statusDict[ID][dictIndex]["numOfEffects"]
            return self.helpCompareLookups(compareStr,numOfEffects,num)
        except:
            print("Error: 'numOfEffects' key not found for the given ID. Ignoring effect.")
            return False
        
    def lookupMassNumOfEffects(self,ID,compareStr,num,allBool,relativeCompareIndex = 0,indices = None):
        boolArr,keyArr = self.helpMassLookup(indices,pauseBool=False,ID=ID)
        try:
            for j in range(len(keyArr)):
                boolArr[j] = self.lookupNumOfEffects(ID,compareStr,num,relativeCompareIndex = 0-j)   
        except:
            print("\nError: you are probably experiencing a key-error.")
            return False
        
        if allBool:
            return all(boolArr)
        else:
            return any(boolArr)
        
        
    def lookupIndex(self,ID,compareStr,idx,relativeCompareIndex = 0):
        dictIndex = self.helpdictIndex(len(self.statusDict[ID]),relativeCompareIndex)
        lookupIdx = self.statusDict[ID][dictIndex]["index"]
        return self.helpCompareLookups(compareStr,lookupIdx,idx)
    
    def lookupRandomNum(self,ID,compareStr,num,relativeCompareIndex = 0):
        try:
            dictIndex = self.helpdictIndex(len(self.statusDict[ID]),relativeCompareIndex)
            randomNum = self.statusDict[ID][dictIndex]["randomNum"]
            return self.helpCompareLookups(compareStr,randomNum,num)
        except:
            print("Error: 'randomNum' key not found for the given ID. Ignoring effect.")
            return False
        
    def helpLookupPosition(self,ID,relativeCompareIndex = 0):
        dictIndex = self.helpdictIndex(len(self.statusDict[ID]),relativeCompareIndex)
        return self.statusDict[ID][dictIndex]["positions"]
    
    def setPositionByID(self,ID,offset = 0,relativeCompareIndex = 0):
        dictIndex = self.helpdictIndex(len(self.statusDict[ID]),relativeCompareIndex)
        return self.statusDict[ID][dictIndex]["positions"] + offset*1000
    
    def comparePositions(self,arrID,op,offset,relativeCompareIndex = 0):
        posArr = [None] * len(arrID)
        for count,i in enumerate(arrID):
            posArr[count] = self.helpLookupPosition(i,relativeCompareIndex)
        return eval(op)(posArr) + offset
        
    
    def lookupName(self,ID,name,relativeCompareIndex = 0):
        dictIndex = self.helpdictIndex(len(self.statusDict[ID]),relativeCompareIndex)
        dictName = self.statusDict[ID][dictIndex]["name"]
        if dictName == name:
            return True
        return False
    
    
    #Lookups for the pause dictionary.
    def lookupNumericalPauseDict(self,pauseIndex,lookupvalue,op,comparevalue):
        try:
            if eval("self.pauseDict['" + str(pauseIndex) + "']['"+lookupvalue+"']" + op + str(comparevalue)):
                return True
            return False
        except:
            print("\nError: you are possibly attempting to use this to compare strings or arrays. Please use another lookup, and ensure that the lookupvalue and the operator are given as strings.\n")
            return False
                
    def lookupMassNumericalPauseDict(self,allBool,lookupvalue,op,comparevalue,indices=None):
        boolArr,keyArr = self.helpMassLookup(indices)
        try:
            for count,j in enumerate(keyArr):
                boolArr[count] = self.lookupNumericalPauseDict(j,lookupvalue,op,comparevalue)   
        except:
            print("\nError: you are probably experiencing a key-error. Did you include index 0 in your list?")
            return False
        if allBool:
            return all(boolArr)
        else:
            return any(boolArr)
                
        
    def lookupStringPauseDict(self,pauseIndex,lookupvalue,comparevalue):
        try:
            if self.pauseDict[pauseIndex][lookupvalue] == comparevalue:
                return True
            return False
        except:
            print("\nError: you can only use this function to compare strings - i.e. 'effectName' or the song name 'name' of the relevant pause.\n")
            return False
        
        #Help function for the mass lookups
    def helpMassLookup(self,indices,pauseBool = True,ID = None):
        
        if pauseBool:
            lookupDict = self.pauseDict
        else:
            lookupDict = self.statusDict[ID]
        
        if indices is None:
            keyArr = list(lookupDict.keys())
            boolArr = [None] * len(keyArr)
        else:
            keyArr = indices
            boolArr = [None] * len(indices)
        return boolArr,keyArr
    
    
    def lookupMassStringPauseDict(self,allBool,lookupvalue,comparevalue,indices=None):
        boolArr,keyArr = self.helpMassLookup(indices)
        
        try:
            for count,j in enumerate(keyArr):
                boolArr[count] = self.lookupStringPauseDict(j,lookupvalue,comparevalue)   
        except:
            print("\nError: you are probably experiencing a key-error. Did you include index 0 in your list?")
            return False
        if allBool:
            return all(boolArr)
        else:
            return any(boolArr)
        
        
    def lookupArrPauseDict(self,pauseIndex,arrOp,lookupvalue,op,comparevalue):
        try:
            if eval(arrOp +"(self.pauseDict['" + str(pauseIndex) + "']['"+lookupvalue+"'])" + op + str(comparevalue)):
                return True
            return False
        except:
            print("\nError: please be sure that you are using the array lookup correctly :)")
            
    def lookupMassArrPauseDict(self,allBool,arrOp,lookupvalue,op,comparevalue,indices=None):
        boolArr,keyArr = self.helpMassLookup(indices)
        
        try:
            for count,j in enumerate(keyArr):
                boolArr[count] = self.lookupArrPauseDict(j,arrOp,lookupvalue,op,comparevalue)   
        except:
            print("\nError: you are probably experiencing a key-error. Did you include index 0 in your list?")
            return False
        if allBool:
            return all(boolArr)
        else:
            return any(boolArr)
        
    def helpLookupEffectPauseDict(self,effectName,lookupvalue,op):
        try:
            keyArr = list(self.pauseDict.keys())
            lookupArr = []
            
            for j in keyArr:
                if self.pauseDict[str(j)]["effectName"] == effectName :
                    val = self.pauseDict[str(j)][lookupvalue]
                    lookupArr.append(val)
            return eval(op)(lookupArr)
        except:
            return 0
        
    
    def helpLookupEffectStatusDict(self,ID,lookupvalue,op):
        try:
            keyArr = list(self.statusDict[ID].keys())
            lookupArr = []
            
            for j in keyArr:
                    val = self.statusDict[ID][j][lookupvalue]
                    lookupArr.append(val)
            return eval(op)(lookupArr)
        except:
            return 0
    
    def lookupCountStatusAndPause(self,ID,effectName,lookupvalue,op,countop,compareStr,compareVal):
        val1 = self.helpLookupEffectPauseDict(effectName,lookupvalue,op)
        val2 = self.helpLookupEffectStatusDict(ID,lookupvalue,op)
        
        arr = [val1,val2]
        opValue = eval(countop)(arr)
        
        return eval(str(opValue) + compareStr + str(compareVal))
    
    ################################################################
    
     #hest
    def generateKlub100(self,randomBool,standardPauseConflictSetting=None):   
        """
        Function to generate the Klub100. Awfully written, please do not look.

        Parameters
        ----------
        randomBool : boolean
            Boolean to determine whether or not the list of songs is randomised or not. If False, the songs used will simply be the first X in the data sheet, where X is the length of the Klub100..
        standardPauseConflictSetting : string, optional
            String to determine a standard setting in case of pause conflict. "IC" or "II" for "ignore custom" or "ignore index".

        """
        self.standardPauseConflictSetting = standardPauseConflictSetting

        songsList = self.initSongs(randomBool,self.songName,self.songs,self.positions)
        self.songsList = songsList
        
        BumsernesKlub100 = AudioSegment.empty()
        BumsernesKlub100 += self.effects["intro"]
        
        print("\nNow stitching the songs...")
        
        #Define ID list and initialise the dictionary that holds the number of times it has been applied
        idList = list(self.conditionsDict.keys())
        countDict = {}
        for ID in idList:
            countDict[ID] = 0
        
        #Loop begin
        i = 0
        songcounter = 1
        while songcounter <= self.length:
            print('Qwabs100 is at song',songcounter,'out of '+str(self.length))
            name = self.songName[songsList[i]]
            # print(name)
            try:
                song = self.loadSoundClip(self.loc + "songs\\" + name + ".mp4")
            except:
                print(name)
                print(songcounter)
                break
            # Adds fade in and fade out to the song
            song = song.fade_in(2000).fade_out(2000)
                                                     
            self.name = name
            self.i = i
            
            #Loops to determine conditional effects. This is a clusterfuck
            for ID in idList:
                callableList = self.conditionsDict[ID][0]
                # print(callableList)
                conditionsBool = True
                
                
                #If-statements in order to determine 1) how many conditions to be called
                # 2) whether any logic should be applied (if depthcount is three, OR-is used)
                if not(isinstance(callableList,list)):
                    func = callableList
                    # print(self.conditionsDict[ID][1])
                    if not func(*self.conditionsDict[ID][1]):
                        conditionsBool = False
                        
                elif self.depthCount(callableList) == 1:
                    for count,func in enumerate(callableList):
                        # print(self.conditionsDict[ID][count])
                        if not func(*self.conditionsDict[ID][1][count]):
                            conditionsBool = False
                            break
                        
                elif self.depthCount(callableList) == 2:
                    conditionsBoolArr = [True] * len(callableList)
                    
                    for orCount,orSettings in enumerate(callableList):
                        for count,func in enumerate(orSettings):
                            if not func(*self.conditionsDict[ID][1][orCount][count]):
                                conditionsBoolArr[orCount] = False
                                break
                                
                    if not(any(conditionsBoolArr)):
                        conditionsBool = False
                # print(conditionsBool)
                #If the conditions are met, we call the functions nested in the dictionary with the relevant settings
                if conditionsBool:
                    localStatusDict = {}

                    settings = self.conditionsDict[ID][2]
                    
                    #If any callables in the settings
                    callSettingsTuple = [(i,s) for i,s in enumerate(settings) if isinstance(s,list) if callable(s[0])]
                    
                    usedSettings = settings.copy()
                    for tuples in callSettingsTuple:
                        idx = tuples[0]
                        funcList = tuples[1]
                        
                        # print(funcList[1:])
                        value = funcList[0](*funcList[1:])
                        usedSettings[idx] = value

                    out = self.conditionsDict[ID][3](song,*usedSettings)
                    if isinstance(out, list):
                        song = out[0]
                        
                
                        #Status outputs to save in a dictionary for other conditions
                        outStrings = out[1]
                        if outStrings is False:
                            continue
                        
                        outSettings = out[2]
                        for k in range(len(outStrings)):
                            localStatusDict[outStrings[k]] = outSettings[k]
                    else:
                        song = out
                    
                    if countDict[ID] == 0:
                        indexedStatusDict = {}
                    else:
                        indexedStatusDict = self.statusDict[ID]
                        
                    
                    localStatusDict["index"] = i
                    localStatusDict["name"] = name

                    indexedStatusDict[countDict[ID]] = localStatusDict
                    self.statusDict[ID] = (indexedStatusDict)
                    
                    countDict[ID] += 1
                    
            #Add a potential mashup
            if self.randomMashAddedBoolean and i < len(self.url)-1:
                chance = self.mashSettings[0]
                effect = self.effects[self.mashSettings[1]]
                # print(i+1)
                # print(len(self.songName)-i-1)
                ranIndex = self.randomInt(i+1,len(self.songName)-1,size=None)
                    
                song = self.randomMashup(chance,song,self.songName[songsList[ranIndex]],effect)
                # i += 1

            #Add either a custom pause or random pause 
            customPause = self.customPause(i,name,song)
            if customPause != False:
                song = customPause
            elif i > 0:
                randomPauseOut = self.insertRandomPause(song)
                if randomPauseOut[0]:
                    song,speeds,numOfEffects,slow,fast,meanMin,meanMax,mean,timeMin,timeMax,time = randomPauseOut[1]
                    effectName = randomPauseOut[2]
                    
                    localPauseDict = {}
                    
                    #The current number of counts for which the effect has been used to make a pause
                    localPauseDict["currentPauseEffectCounts"] = self.pauseCounterDict[effectName]
                    
                    localPauseDict["name"] = name
                    localPauseDict["effectName"] = effectName
                    localPauseDict["speeds"] = speeds
                    localPauseDict["numOfEffects"] = numOfEffects
                    localPauseDict["slow"] = slow
                    localPauseDict["fast"] = fast
                    localPauseDict["meanMin"] = meanMin
                    localPauseDict["meanMax"] = meanMax
                    localPauseDict["mean"] = mean
                    localPauseDict["timeMin"] = timeMin
                    localPauseDict["timeMax"] = timeMax
                    localPauseDict["time"] = time
                    
                    self.pauseDict[str(songcounter)] = localPauseDict

            i += 1
            songcounter += 1
            BumsernesKlub100 += song
        #Loop end
        
        # Adds the outro file to the output file
        BumsernesKlub100 += self.effects["outro"]
        print("Done sticthing. Now exporting the file - this might take some time.\n")

        # Exports the output file
        BumsernesKlub100.export(self.loc + 'BumsernesKlub100_seed{}'.format(self.seed) + '.mp4',format="mp4")
        print('Seed used was {}'.format(self.seed))
        print('bonsjuar madame')
           
        ################################################################
    
    def lookupLatestIndexByID(self,ID):
        try:
            dictIndex = self.helpdictIndex(len(self.statusDict[ID]),0)
            if self.statusDict[ID][dictIndex]["index"] == self.i:
                return True
            return False
        except:
            return False
    
    def lookupLengthOfDictionary(self,ID,compareStr,compareval):
        try:
            ln = len(self.statusDict[ID])
            return eval(str(ln) + compareStr + str(compareval))
        except:
            if compareStr == "<":
                return True
            elif compareStr == ">":
                return False
            else:
                return False