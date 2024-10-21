# load the libraries that we'll use
import glob
from loguru import logger
import mutagen.id3
import numpy as np
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TALB, TIT2, TIT3, TPE1, TRCK, TYER
from mutagen.mp3 import MP3

# For supported easyid3 tags:
# https://github.com/quodlibet/mutagen/blob/master/mutagen/easyid3.py
# Check out somewhere at end of above linked file


def read_id3_tags(file):
    try:
        audio = MP3(file, ID3=EasyID3)
        return audio.tags

    except Exception as e:
        logger.error(e)


def write_id3_tags(file, tags):
    try:
        audio = MP3(file, ID3=EasyID3)
        for k, v in tags.items():
            audio[k] = v
        audio.save()
    except Exception as e:
        logger.error(e)


# filez = glob.glob("hmtc/utils/working_audio_file.mp3")
# new_tag = {}
# new_tag["date"] = "2021"
# new_tag["artist"] = "Harry Mack"
# new_tag["albumartist"] = ["Harry Mack", "Beardyman", "Leen"]
# new_tag["album"] = "Beardyman in London 1"
# new_tag["title"] = "Leen has entered the chat"
# new_tag["tracknumber"] = ["4", "8"]  # track number/total tracks
# new_tag["albumsort"] = "Beardyman in London 001"
# new_tag["titlesort"] = "Leen has entered the chat"


# id3 = write_id3_tags(file=filez[0], tags=new_tag)
# mp3file = MP3(filez[0], ID3=EasyID3)
# print(mp3file.pprint())
