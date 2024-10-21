from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.models import (
    Section as SectionModel,
)
from hmtc.models import (
    Track as TrackModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.track import TrackItem


def test_track():
    track = TrackModel.create(title="test", track_number=1)
    assert track is not None


def test_delete_track():
    track = TrackModel.create(title="test", track_number=1)
    assert TrackModel.get_or_none(TrackModel.title == "test") is not None
    track.delete_instance()
    assert TrackModel.get_or_none(TrackModel.title == "test") is None


def test_album_create_track():
    album = AlbumModel.create(title="test")
    album_item = AlbumItem.from_model(album)

    album_item.create_track(title="test", length=100)
    album_item.create_track(title="test2", length=300)
    album_item.create_track(title="test3", length=500)

    assert album is not None
    assert album.tracks == 3
    assert album.tracks[0].title == "test"
    assert album.tracks[1].title == "test2"
    assert album.tracks[2].title == "test3"
    assert album.tracks[0].track_number == 1
    assert album.tracks[1].track_number == 2
    assert album.tracks[2].track_number == 3
    logger.error(album.tracks)


def test_remove_track():
    album = AlbumModel.create(title="test")
    album_item = AlbumItem.from_model(album)
    album_item.create_track(title="test", length=100)
    album_item.create_track(title="test2", length=300)
    album_item.create_track(title="test3", length=500)
    album_item.remove_track(id=album.tracks[1].id)
    assert album.tracks == 2
    assert album.tracks[0].title == "test"
    assert album.tracks[1].title == "test3"
    assert album.tracks[0].track_number == 1
    assert album.tracks[1].track_number == 2
    logger.error(album.tracks)


def test_new_track_file(test_audio_filename):
    video = VideoModel.create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
    )
    sec = SectionModel.create(start=0, end=150000, video=video)
    album = AlbumModel.create(title="test")
    track = TrackModel.create(title="test", track_number=1, album=album)
    sec.track = track
    sec.save()
    track_item = TrackItem.from_model(track)
    track_path = track_item.write_file(input_file=test_audio_filename)
    assert track_path != ""
    new_file = FileManager.add_path_to_track(path=track_path, track=track, video=video)
    assert new_file.track_id == track.id
    assert new_file is not None
