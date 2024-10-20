from loguru import logger
from hmtc.models import (
    Section as SectionModel,
)

from hmtc.models import Album as AlbumModel
from hmtc.models import (
    Track as TrackModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.album import Album as AlbumItem
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

    album_item.create_track(title="test")
    album_item.create_track(title="test2")
    album_item.create_track(title="test3")

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
    album_item.create_track(title="test")
    album_item.create_track(title="test2")
    album_item.create_track(title="test3")
    album_item.remove_track(id=album.tracks[1].id)
    assert album.tracks == 2
    assert album.tracks[0].title == "test"
    assert album.tracks[1].title == "test3"
    assert album.tracks[0].track_number == 1
    assert album.tracks[1].track_number == 2
    logger.error(album.tracks)
