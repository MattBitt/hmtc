from datetime import datetime

import pytest
from loguru import logger

from hmtc.models import *


def test_create_poster_file(poster_file_dicts):
    poster = ImageFile.create(**poster_file_dicts[0])
    assert poster.height == poster_file_dicts[0]["height"]
    assert poster.width == poster_file_dicts[0]["width"]
    assert poster.colorspace == poster_file_dicts[0]["colorspace"]


def test_create_audio_file(audio_file_dicts):
    audio = AudioFile.create(**audio_file_dicts[0])
    assert audio.bitrate == audio_file_dicts[0]["bitrate"]
    assert audio.sample_rate == audio_file_dicts[0]["sample_rate"]
    assert audio.channels == audio_file_dicts[0]["channels"]
    assert audio.duration == audio_file_dicts[0]["duration"]


def test_create_video_file(video_file_dicts):
    video = VideoFile.create(**video_file_dicts[0])
    assert video.duration == video_file_dicts[0]["duration"]
    assert video.frame_rate == video_file_dicts[0]["frame_rate"]
    assert video.width == video_file_dicts[0]["width"]
    assert video.height == video_file_dicts[0]["height"]
    assert video.codec == video_file_dicts[0]["codec"]


def test_track_audio_file(track_item, audio_file_dicts):
    audio = AudioFile.create(**audio_file_dicts[0])
    track_item.add_file(audio.path)
    _audio_file = track_item.get_file("audio")
    assert _audio_file is not None
    track_item.delete_file("audio")
    _audio_file2 = track_item.get_file("audio")
    assert _audio_file2 is None
