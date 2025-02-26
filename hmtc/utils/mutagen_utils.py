# load the libraries that we'll use
import glob
from pathlib import Path

import mutagen.id3
import numpy as np
from loguru import logger
from mutagen.easyid3 import EasyID3

# For supported easyid3 tags:
# https://github.com/quodlibet/mutagen/blob/master/mutagen/easyid3.py
# Check out somewhere at end of above linked file
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, TALB, TIT2, TIT3, TPE1, TRCK, TYER, PictureType
from mutagen.mp3 import MP3

from hmtc.config import init_config
from hmtc.utils.image import convert_webp_to_png
from mutagen.mp4 import MP4, MP4Cover

config = init_config()
WORKING = Path(config["WORKING"])
STORAGE = Path(config["STORAGE"])


def embed_image(audio_file: Path, image_file: Path):
    """Embeds an image into an audio file."""
    audio_file = str(audio_file)
    image_file = image_file
    need_to_delete = False
    if str(image_file).endswith(".webp"):
        image_file = convert_webp_to_png(file=image_file, path=WORKING)
        need_to_delete = True

    if str(audio_file).endswith(".flac"):
        audio = FLAC(audio_file)

        # Create a Picture object
        picture = Picture()
        with open(image_file, "rb") as f:
            picture.data = f.read()
        picture.type = 3  # Front cover
        picture.mime = "image/jpeg"  # Or "image/png"

        # Add the picture to the FLAC metadata
        audio.add_picture(picture)

    elif str(audio_file).endswith(".mp3"):
        audio = ID3(audio_file)

        # Create an APIC frame
        with open(image_file, "rb") as f:
            image_data = f.read()
        if str(image_file).endswith(".jpg") or str(image_file).endswith(".jpeg"):
            _mime = "image/jpeg"
        elif str(image_file).endswith(".png"):
            _mime = "image/png"
        else:
            raise ValueError(f"Unsupported image format {image_file}")
        apic = APIC(
            encoding=3,  # UTF-8
            mime=_mime,
            type=3,  # Front cover
            desc="Cover",
            data=image_data,
        )

        # Add the APIC frame to the MP3 metadata
        audio.add(apic)

    else:
        raise ValueError("Unsupported file format")

    audio.save()
    if need_to_delete:
        image_file.unlink()



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

def write_mp4_metadata(file: Path, tags: dict):
    taggerMP4 = MP4(file)

    taggerMP4.delete()
    taggerMP4.save()
    print(taggerMP4.pprint())
    taggerMP4["xa9ART"] = ["Harry Mack"]
    
    taggerMP4["aART"] = ["Harry Mack"] + ([tags['artist']] if 'artist' in tags else [])
    taggerMP4["soaa"] = ["Mack, Harry"] # album artist sort order
    
    taggerMP4["xa9alb"] = tags['album_title'] # album
    taggerMP4["soal"] = tags.get("album_title_sort", tags["album_title"]) # album sort
    
    taggerMP4["xa9nam"] = tags['track_title'] # track title
    taggerMP4["sonm"] = tags.get("track_title_sort", tags["track_title"]) # title sort
    taggerMP4["xa9day"] = tags['upload_date']
    taggerMP4['trkn'] = [(int(tags['track_number']), 0)] # track number
    taggerMP4['disk'] = [(int(tags['disc_number']), 0)] # disc number
    
    taggerMP4.save()
    print(taggerMP4.pprint())

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
# embed_image("hmtc/utils/working_audio_file.mp3", "hmtc/utils/working_image.png")
if __name__ == "__main__":
    tags = {
        "artist": "Podcast Host",
        "album_title": "Flow State",
        "track_title": "OB 58.3 - chocolate.mp4",
        "track_number": "3",
        "disc_number": "2",
        "upload_date": "2024-09-23",
    }

    # file = "/home/matt/apps/data_for_development/hmtc/development/storage/libraries/video/Harry Mack/Flow State/Disc 002/OB 58.3 - chocolate.mp4"
    # write_mp4_metadata(file=Path(file), tags=tags)

    id3_tags = {}
    id3_tags["date"] = "2021"
    id3_tags["originaldate"] = "2021-01-03"
    id3_tags["artist"] = "Harry Mack"
    id3_tags["albumartist"] = ["Harry Mack"]
    id3_tags["album"] = "Flow State"
    id3_tags["title"] = "banana"
    id3_tags["tracknumber"] = "1"
    id3_tags["discnumber"] = "6"
    id3_tags["albumsort"] = "Flow State"
    id3_tags["titlesort"] = "banana"
    file = "/home/matt/apps/data_for_development/hmtc/development/storage/libraries/audio/Harry Mack/Flow State/Disc 001/OB 57.1 - banana.mp3"
    write_id3_tags(file, id3_tags)