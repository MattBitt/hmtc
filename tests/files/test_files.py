from hmtc.models import *
import pytest
from datetime import datetime

@pytest.fixture
def file_dicts():
    return [
        {
            'path': '/path/to/file1.txt',
            'file_size': 1024,
            'modified_date': '2023-01-01 00:00:00',
            'mime_type': 'text/plain',
            'hash': 'abc123'
        },
        {
            'path': '/path/to/file2.txt',
            'file_size': 2048,
            'modified_date': '2023-01-02 00:00:00',
            'mime_type': 'text/plain',
            'hash': 'def456'
        }
    ]

@pytest.fixture
def poster_file_dicts():
    return [
        {
            'path': '/path/to/poster1.jpg',
            'file_size': 1024000,
            'modified_date': '2023-01-01 00:00:00',
            'mime_type': 'image/jpeg',
            'hash': 'poster123',
            'height': 1080,
            'width': 1920,
            'colorspace': 'RGB'
        },
        {
            'path': '/path/to/poster2.jpg',
            'file_size': 2048000,
            'modified_date': '2023-01-02 00:00:00',
            'mime_type': 'image/jpeg',
            'hash': 'poster456',
            'height': 720,
            'width': 1280,
            'colorspace': 'RGB'
        }
    ]

@pytest.fixture
def audio_file_dicts():
    return [
        {
            'path': '/path/to/audio1.mp3',
            'file_size': 5120000,
            'modified_date': '2023-01-01 00:00:00',
            'mime_type': 'audio/mpeg',
            'hash': 'audio123',
            'bitrate': 320,
            'sample_rate': 44100,
            'channels': 2,
            'duration': 180
        },
        {
            'path': '/path/to/audio2.mp3',
            'file_size': 7680000,
            'modified_date': '2023-01-02 00:00:00',
            'mime_type': 'audio/mpeg',
            'hash': 'audio456',
            'bitrate': 192,
            'sample_rate': 48000,
            'channels': 2,
            'duration': 240
        }
    ]

@pytest.fixture
def video_file_dicts():
    return [
        {
            'path': '/path/to/video1.mp4',
            'file_size': 102400000,
            'modified_date': '2023-01-01 00:00:00',
            'mime_type': 'video/mp4',
            'hash': 'video123',
            'duration': 300,
            'frame_rate': 29.97,
            'width': 1920,
            'height': 1080,
            'codec': 'h264'
        },
        {
            'path': '/path/to/video2.mp4',
            'file_size': 204800000,
            'modified_date': '2023-01-02 00:00:00',
            'mime_type': 'video/mp4',
            'hash': 'video456',
            'duration': 600,
            'frame_rate': 60,
            'width': 3840,
            'height': 2160,
            'codec': 'h265'
        }
    ]


@pytest.fixture
def poster_file_item(poster_file_dicts):
    poster = PosterFile.create(**poster_file_dicts[0])
    yield poster
    poster.delete()

@pytest.fixture
def audio_file_item(audio_file_dicts):
    audio = AudioFile.create(**audio_file_dicts[0])
    yield audio
    audio.delete()

@pytest.fixture
def video_file_item(video_file_dicts):
    video = VideoFile.create(**video_file_dicts[0])
    yield video
    video.delete()

@pytest.fixture
def album_files_item(album_item, poster_file_item):
    album_files = AlbumFiles.create({
        'item_id': album_item.instance.id,
        'poster_file_id': poster_file_item.instance.id
    })
    yield album_files
    album_files.delete()

@pytest.fixture
def video_files_item(video_item, poster_file_item, video_file_item, audio_file_item):
    video_files = VideoFiles.create(**{
        'item_id': video_item.instance.id,
        'poster_file_id': poster_file_item.instance.id,
        'video_file_id': video_file_item.instance.id,
        'audio_file_id': audio_file_item.instance.id
    })
    yield video_files
    video_files.delete()

def test_create_poster_file(poster_file_item, poster_file_dicts):
    assert poster_file_item.height == poster_file_dicts[0]['height']
    assert poster_file_item.width == poster_file_dicts[0]['width']
    assert poster_file_item.colorspace == poster_file_dicts[0]['colorspace']

def test_create_audio_file(audio_file_item, audio_file_dicts):
    assert audio_file_item.bitrate == audio_file_dicts[0]['bitrate']
    assert audio_file_item.sample_rate == audio_file_dicts[0]['sample_rate']
    assert audio_file_item.channels == audio_file_dicts[0]['channels']
    assert audio_file_item.duration == audio_file_dicts[0]['duration']

def test_create_video_file(video_file_item, video_file_dicts):
    assert video_file_item.duration == video_file_dicts[0]['duration']
    assert video_file_item.frame_rate == video_file_dicts[0]['frame_rate']
    assert video_file_item.width == video_file_dicts[0]['width']
    assert video_file_item.height == video_file_dicts[0]['height']
    assert video_file_item.codec == video_file_dicts[0]['codec']

def test_album_files_relationship(album_files_item):
    assert album_files_item.poster_file is not None
    assert album_files_item.poster_file.height == poster_file_dicts[0]['height']

def test_video_files_relationship(video_files_item):
    assert video_files_item.video_file is not None
    assert video_files_item.audio_file is not None
    assert video_files_item.poster_file is not None
    assert video_files_item.video_file.codec == video_file_dicts[0]['codec']
    assert video_files_item.audio_file.bitrate == audio_file_dicts[0]['bitrate']
