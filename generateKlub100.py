#%%
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
os.chdir(file_dir)

from klub100logic import klub100

#Der følger en lille guide nedenfor. 
#bemærk, at du kan bruge python-scriptet "generateshoutouts.py", hvis du gerne vil downloade shoutouts
#fra google translate som f.eks. enkelte effekter eller til mapper. 





# scriptet kan hente sange fra youtube eller soundcloud (og en masse andre, se dokumentation for "youtube-dl").
# scriptet henter links fra enten en lokal excel-fil "localbool = true", eller google sheets "localbool = false".
# hvis du ønsker at den skal hente fra google sheets, kræver det, at du følger nedenstående guide:
    # https://developers.google.com/sheets/api/quickstart/python
    # (hvis du bare vil kunne hente fra mit sheet kræver det, at jeg tilføjer din mail som autoriseret - skriv)
    
#scriptet henter automatisk manglende sange og shoutouts til "effects"-mappen.
#hvis du ønsker at bruge en effekt, angives navnet på den som en streng (uden extension)
#eller "dir-*mappenavn*", hvis det er en mappe med lydeffekter.


#der kan tilføjes lydeffekter dynamisk med addcondition-funktionen.
#der kan samtidig gives dynamiske indstillinger til de funktioner, der tilføjer lydeffekter. se eksempler nedenfor.
#syntaksen i disse tilfælde er [funtkion,args]. så kaldes funktionen med de argumenter, når lydfilen stitches.
#bemærk, at funktionen skal returnere true eller false, hvis den bruges som condition. det er "lookup"-funktionerne.
#med tre nestede lister laver man or-logik - så [ [[f1,i1,i2]],[[f2,i1,i2]] ] bliver true, hvis enten f1 eller f2 er sande.


###########################################################################


#angiv stien til din klub100. her genereres filen, og alle mapper oprettes.
# loc = "C:\\Users\\mfrue\\OneDrive - Danmarks Tekniske Universitet\\Privat\\Klub100\\racisterne\\"
# localexcelname = "k100.xlxs"

loc = "C:\\Users\\mfrue\\OneDrive - Danmarks Tekniske Universitet\\Privat\\Klub100\\racisterne\\"

#længden af din klub99
length = 100 
test = klub100(loc,length=length,localBool=False,lan=None)





# #tilføj sandsynlighed fffffffffor at en given sang tilfældigt overlayes med en anden
# test.addRandomMash(0.5,"mashup")

# #tilføj bestemt effekt når der er afspillet flere end 1000 af en mashed effekt
# test.addSoundOverlay("qwabs1000gange",positions=0,ID="1000kwabs")
# test.addCondition("1000kwabs",[[test.lookupLengthOfDictionary,"1000kwabs","<",1],[test.lookupCountStatusAndPause, "rankwabs","kwabs","numofeffects","sum","sum",">",1000]])

# #tving sang i den tilfældige liste
test.addForcedSongs(["helmig","cat","de ja vu","glad i bad","BONSJUAR MADAM","BONSJUAR MADAM","BONSJUAR MADAM","BONSJUAR MADAM","BONSJUAR MADAM","BONSJUAR MADAM"])

# #overlay en mappe med effekter på specifikke positioner hvis sangnavnet for en given sang er "helmig"
# test.addSoundOverlay("DIR-pat", [30.5,36.5,42.5,48,53.5],ID="helmig",db=0)
# test.addCondition("helmig", [test.lookupCurrentSongName,"helmig"])

# #2 procent chance for at en sang bliver dobbelt hastighed og afspilles en effekt "turbomode" inden.
# test.addRandomSpeedChange(0.02,2,"turbomode")

# #samme som ovenfor, bare halv hastighed og med anden effekt.
# test.addRandomSpeedChange(0.02,0.5,"skildpadde")

# #100 procent chance for dobbelt hastighed på sangen "de ja vu".
# test.addRandomSpeedChange(1,2,ID = "dejavu")
# test.addCondition("dejavu",[test.lookupCurrentSongName,"de ja vu"])

# #tilføj tilfældige overlays på en sang hvor de mashes sammen. der er mange indstillinger til denne funktion.
test.addRandomOverlaySound(0.09,"kwabs",mashBool=True)
# test.addRandomOverlaySound(0.1,"hello",mashBool=True,ID="ranhello",db=0,slow = 0.8,fast=1.5)

# #tilføj en tilfældig effekt fra en fast mappe hvis den laveste hastighed i et mashed tilfældigt kli er under 0.25.
# #lookupspeen sammenholder med en liste med hastigheder fra seneste effekt og regner som standard minimum.
# #man kan også give den et argument som ex. "sum", hvis det skal være summen af hastigheder.
# test.addSoundOverlay([test.randomSoundEffect,"DIR-bund"],[test.setPositionByID,"rankwabs",1],ID="bundspeed")
# test.addCondition("bundspeed",[test.lookupSpeed,"rankwabs","<",0.25])


# #tilføj tilfældig lydeffekt fra fast mappe og sæt den på en given position 
# #hvis lydeffekterne forbundet med rankwabs og ranhello er afspillet i den nuværende iteration.
# test.addSoundOverlay([test.randomSoundEffect,"DIR-bund"],[test.comparePositions,["rankwabs","ranhello"],"max",1000],ID="bundclip")
# test.addCondition("bundclip",[[test.lookupLatestIndexByID,"rankwabs"],[test.lookupLatestIndexByID,"ranhello"]])
                     
# #tilføj pauser. limietd pauser stopper med at blive tilføjet, når alle effekterne er brugt én gang.
# #første argument er vægte; det er tilfældigt hvilken pause tilføjes.
# #hvis man ønsker deterministiske pauser skal man benytte sig af mapperne "pauses-index" eller "pauses-songname".
# test.addLimitedPause(0.15,"DIR-michael")
# test.addLimitedPause(0.3,"DIR-shoutout")
# test.addRandomMashedPause(0.55,"kwabs") 

# #generer klub100 med tilfældige sange.
# test.generateKlub100(randomBool = True)

# #hello

#100 procent chance for dobbelt hastighed på sangen "de ja vu".
test.addRandomSpeedChange(1,2,ID = "dejavu")
test.addCondition("dejavu",[test.lookupCurrentSongName,"de ja vu"])

# test.addRandomSpeedChange(1,2,ID = "thjalfe")
# test.addCondition("thjalfe",[test.lookupCurrentSongName,"papvin"])

# test.addRandomSpeedChange(1,0.6,ID = "seegert")
# test.addCondition("seegert",[test.lookupCurrentSongName,"solhverv"])

# test.addRandomOverlaySound(1,"lassegrin",mashBool=False,ID="lassegrin1",db=0)
# test.addRandomOverlaySound(1,"lassegrin",mashBool=False,ID="lassegrin2",db=0)
# test.addRandomOverlaySound(1,"lassegrin",mashBool=False,ID="lassegrin3",db=0)

# test.addCondition("lassegrin1",[test.lookupCurrentSongName,"lasse"])
# test.addCondition("lassegrin2",[test.lookupCurrentSongName,"lasse"])
# test.addCondition("lassegrin3",[test.lookupCurrentSongName,"lasse"])


test.addLimitedPause(0.20,"DIR-michael") 
test.addLimitedPause(1,"DIR-shoutout")
# test.addLimitedPause(1,"fisse")
# test.addRandomMashedPause(0.17,"fisse",slow=0.85,fast=1.2,meanMin=2,meanMax=4) 
# test.addRandomMashedPause(0.17,"dø",slow=0.85,fast=1.2,meanMin=2,meanMax=4) 
test.addRandomMashedPause(0.05,"heste",slow=0.85,fast=1.2,meanMin=2,meanMax=4)

test.addRandomMashedPause(0.05,"kwabs", slow = 0.5, fast = 1.5) 

test.addSoundOverlay("DIR-pat", [30.5,36.5,42.5,48,53.5],ID="helmig",db=0)
test.addCondition("helmig", [test.lookupCurrentSongName,"helmig"])

# #generer klub100 med tilfældige sange
test.generateKlub100(randomBool = True)

# %%
