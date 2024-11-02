import pytest
from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.models import (
    Section as SectionModel,
)
from hmtc.models import SectionTopics as SectionTopicsModel
from hmtc.models import Topic as TopicModel
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


@pytest.mark.xfail(reason="Currently failing due to missing image file?")
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
    track_path = track_item.write_audio_file(input_file=test_audio_filename)
    assert track_path != ""
    new_file = FileManager.add_path_to_track(path=track_path, track=track, video=video)
    assert new_file.track_id == track.id
    assert new_file is not None


def test_new_track_from_section(test_audio_filename):
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
    album = AlbumModel.create(title="test")
    album_item = AlbumItem.from_model(album)

    sec = SectionModel.create(start=0, end=150000, video=video)

    track_item = album_item.create_from_section(section=sec, video=video)
    assert track_item is not None
    assert track_item.title == video.title
    assert track_item.length == 150
    section_to_check = (
        SectionModel.select(SectionModel.id, SectionModel.track_id)
        .where(SectionModel.id == sec.id)
        .get()
    )
    assert section_to_check.track.id == track_item.id
    topic = TopicModel.create(text="bottle")
    topic2 = TopicModel.create(text="orange")
    topic3 = TopicModel.create(text="supercalifragilisticexpialidocious")
    SectionTopicsModel.create(section=sec, topic=topic, order=1)
    SectionTopicsModel.create(section=sec, topic=topic2, order=2)
    SectionTopicsModel.create(section=sec, topic=topic3, order=3)
    sec2 = SectionModel.select().where(SectionModel.id == sec.id).get()
    assert sec2 is not None
    track_item2 = album_item.create_from_section(section=sec2, video=video)
    assert track_item2 is not None
    # 40 characters and then ...
    assert track_item2.title == "bottle, orange, supercalifragilisticexpi..."
