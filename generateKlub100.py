import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
os.chdir(file_dir)

from klub100logic import Klub100

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


#Der kan tilføjes lydeffekter dynamisk med addCondition-funktionen.
#Der kan samtidig gives dynamiske indstillinger til de funktioner, der tilføjer lydeffekter. Se eksempler nedenfor.
#Syntaksen i disse tilfælde er [funtkion,args]. Så kaldes funktionen med de argumenter, når lydfilen stitches.
#Bemærk, at funktionen skal returnere True eller False, hvis den bruges som condition. Det er "lookup"-funktionerne.
#Med tre nestede lister laver man OR-logik - så [ [[F1,i1,i2]],[[F2,i1,i2]] ] bliver True, hvis enten F1 eller F2 er sande.


###########################################################################


#Angiv stien til din Klub100. Her genereres filen, og alle mapper oprettes.
loc = "C:\\Users\\Marcus\\OneDrive - Danmarks Tekniske Universitet\\klub200\\"
localExcelName = "k100.xlxs"

#Længden af din Klub100
length = 1

#Initialiser klub100 objektet
test = Klub100(loc,length=length,localBool=False)

#Tilføj sandsynlighed for at en given sang tilfældigt overlayes med en anden
test.addRandomMash(0.01,"mashup")

#Tilføj bestemt effekt når der er afspillet flere end 1000 af en mashed effekt
test.addSoundOverlay("qwabs1000gange",positions=0,ID="1000kwabs")
test.addCondition("1000kwabs",[[test.lookupLengthOfDictionary,"1000kwabs","<",1],[test.lookupCountStatusAndPause, "ranKwabs","kwabs","numOfEffects","sum","sum",">",1000]])

#Tving sang i den tilfældige liste
test.addForcedSongs(["helmig","cat","de ja vu"])

#Overlay en mappe med effekter på specifikke positioner hvis sangnavnet for en given sang er "helmig"
test.addSoundOverlay("DIR-pat", [30.5,36.5,42.5,48,53.5],ID="helmig",db=0)
test.addCondition("helmig", [test.lookupCurrentSongName,"helmig"])

#2 procent chance for at en sang bliver dobbelt hastighed og afspilles en effekt "turbomode" inden.
test.addRandomSpeedChange(0.02,2,"turbomode")

#Samme som ovenfor, bare halv hastighed og med anden effekt.
test.addRandomSpeedChange(0.02,0.5,"skildpadde")

#100 procent chance for dobbelt hastighed på sangen "de ja vu".
test.addRandomSpeedChange(1,2,ID = "dejavu")
test.addCondition("dejavu",[test.lookupCurrentSongName,"de ja vu"])

#Tilføj tilfældige overlays på en sang hvor de mashes sammen. Der er mange indstillinger til denne funktion.
test.addRandomOverlaySound(0.2,"kwabs",mashBool=True,ID="ranKwabs",db=0)
test.addRandomOverlaySound(0.1,"hello",mashBool=True,ID="ranHello",db=0,slow = 0.8,fast=1.5)

#Tilføj en tilfældig effekt fra en fast mappe hvis den laveste hastighed i et mashed tilfældigt kli er under 0.25.
#lookupSpeen sammenholder med en liste med hastigheder fra seneste effekt og regner som standard minimum.
#Man kan også give den et argument som ex. "sum", hvis det skal være summen af hastigheder.
test.addSoundOverlay([test.randomSoundEffect,"DIR-bund"],[test.setPositionByID,"ranKwabs",1],ID="bundSpeed")
test.addCondition("bundSpeed",[test.lookupSpeed,"ranKwabs","<",0.25])


#Tilføj tilfældig lydeffekt fra fast mappe og sæt den på en given position 
#hvis lydeffekterne forbundet med ranKwabs og ranHello er afspillet i den nuværende iteration.
test.addSoundOverlay([test.randomSoundEffect,"DIR-bund"],[test.comparePositions,["ranKwabs","ranHello"],"max",1000],ID="bundclip")
test.addCondition("bundclip",[[test.lookupLatestIndexByID,"ranKwabs"],[test.lookupLatestIndexByID,"ranHello"]])
                     
#Tilføj pauser. Limietd pauser stopper med at blive tilføjet, når alle effekterne er brugt én gang.
#Første argument er vægte; det er tilfældigt hvilken pause tilføjes.
#Hvis man ønsker deterministiske pauser skal man benytte sig af mapperne "pauses-index" eller "pauses-songname".
test.addLimitedPause(0.15,"DIR-michael")
test.addLimitedPause(0.3,"DIR-shoutout")
test.addRandomMashedPause(0.55,"kwabs") 

#Generer klub100 med tilfældige sange.
test.generateKlub100(randomBool = True)
