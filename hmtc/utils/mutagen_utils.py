# load the libraries that we'll use
import glob

import mutagen.id3
import numpy as np
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TALB, TIT2, TIT3, TPE1, TRCK, TYER
from mutagen.mp3 import MP3

filez = glob.glob("hmtc/utils/working_audio_file.mp3")
mp3file = MP3(filez[0], ID3=EasyID3)
# what is contained in the existing ID3 tags?
mp3file["artist"] = "New Artist"
mp3file["title"] = "New Title"
mp3file["albumartist"] = ["Punk-O-Rama Vol. 1"]
mp3file["album"] = "New Album"
mp3file.save()
print("Artist:", mp3file["artist"][0])
print("Title:", mp3file["title"][0])
print("Album:", mp3file["album"][0])
print(mp3file)
