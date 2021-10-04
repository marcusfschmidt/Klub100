from gtts import gTTS as gt
loc = "C:\\Users\\mfrue\\OneDrive - Danmarks Tekniske Universitet\\Klub100\\"

sound = gt("tillykke, du har nu hørt kwabs 1000 gange",lang="da")
sound.save(loc + "effects\\qwabs1000gange.mp3") 
