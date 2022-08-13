#%%
from gtts import gTTS as gt

loc = "C:\\Users\\mfrue\\OneDrive - Danmarks Tekniske Universitet\\Privat\\Klub100\\racisterne\\"

sound = gt("intro",lang="da")
sound.save(loc + "effects\\intro.mp3") 




sound = gt("farvel")
sound.save(loc + "effects\\outro.mp3")


