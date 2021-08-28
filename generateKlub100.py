import Klub100Logic as Klub100

#Der følger en lille guide nedenfor. 

#Bemærk, at du kan bruge python-scriptet "generateShoutouts.py", hvis du gerne vil downloade shoutouts
#fra Google Translate som f.eks. enkelte effekter eller til mapper. 




# Scriptet kan hente sange fra YouTube eller Soundcloud (og en masse andre, se dokumentation for "youtube-dl").
# Scriptet henter links fra enten en lokal excel-fil "localBool = True", eller Google Sheets "localBool = False".
# Hvis du ønsker at den skal hente fra Google Sheets, kræver det, at du følger nedenstående guide:
    # https://developers.google.com/sheets/api/quickstart/python
    # (hvis du bare vil kunne hente fra mit Sheet kræver det, at jeg tilføjer din mail som autoriseret - skriv)
    
#Scriptet henter automatisk manglende sange og shoutouts til "effects"-mappen.
#Hvis du ønsker at bruge en effekt, angives navnet på den som en streng (uden extension)
#eller "DIR-*mappenavn*", hvis det er en mappe med lydeffekter.

#Angiv stien til din Klub100. Her genereres filen, og alle mapper oprettes.
loc = "C:\\Users\\Marcus\\OneDrive - Danmarks Tekniske Universitet\\klub200\\"

#Længden af din Klub100
length = 3

#
test = Klub100(loc,length=length,standardPauseConflictSetting="IC",localBool=False,seed=31781)


# Tag ikke fejl, det her er noget forfærdeligt lort
# test.addSoundOverlay('helmig', test.effects["DIR-pat"], [30.5,36.5,42.5,48,53.5])
# test.addForcedSongs(["helmig","cat"],[0,2])
# # test.addRandomMash(1,test.effects["mashup"])

# test.addRandomSpeedChange(0.5,2,test.effects["turbomode"],ID="hest")
# test.addCondition("hest",[
#     [test.lookupCurrentSongName,"helmig"]
#                           ])

test.addRandomOverlaySound(1,"kwabs",mashBool=True,ID="hest",slow=0.1,fast=1,)
# test.addCondition("hest",[
#     [[test.lookupCurrentSongName,"helmig"]],
#     [[test.lookupCurrentSongName,"cat"]]
#     ])

test.addRandomOverlaySound(1,"DIR-bund",ID="bund")
# settings1 = [[test.lookupSongNameByRelativeIndex,"helmig",-1]]
# settings2 = [[test.lookupSongNameByRelativeIndex,"helmig",+1]]
test.addCondition("bund",[test.lookupMassNumOfEffects, "hest", ">", 12,True])


# test.addLimitedPause(0.5,"DIR-bund")
test.addRandomMashedPause(0.5,"kwabs") 



#michael resourcer
test.generateKlub100(test.url,test.songName,randomBool=True)
