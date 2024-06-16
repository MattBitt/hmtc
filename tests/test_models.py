from pathlib import Path

import peewee
import pytest
from loguru import logger

from hmtc.config import init_config
from hmtc.db import seed_database
from hmtc.models import (
    Channel,
    File,
    Playlist,
    Section,
    Series,
    TodoTable,
    Video,
    get_file_type,
)

config = init_config()


def test_empty_db():
    assert len(Playlist.select()) == 0
    assert len(Channel.select()) == 0
    assert len(Series.select()) == 0
    assert len(Video.select()) == 0
    assert len(File.select()) == 0
    assert len(Section.select()) == 0


def test_seed_database():
    seed_database()
    assert len(Channel.select()) > 0
    assert len(Playlist.select()) > 0

    assert len(Series.select()) > 0


def test_series():
    s, created = Series.get_or_create(
        name="test", start_date="2020-01-01", end_date="2020-12-31"
    )
    assert created is True
    assert s.name == "test"

    all_series = Series.select()
    assert all_series.count() == 1
    logger.debug(f"all_series.count() = {all_series.count()}")
    s.delete_instance()


# this test leaves a record in the database
def test_permanance_setup():
    s = Series.create(name="testing permanent record")
    assert s is not None


def test_permanance_execute():
    s = Series.get_or_none(Series.name == "testing permanent record")
    assert s is None


def test_channel():
    Channel.create_table()
    c, created = Channel.get_or_create(
        name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;"
    )
    assert c.name == "test"
    assert created is True

    c.delete_instance()


def test_playlist():
    Playlist.create_table()
    p, created = Playlist.get_or_create(
        title="test", url="www.yahoo.com/playlists", youtube_id="PLTvadsfadghas"
    )
    assert created is True
    assert p.title == "test"

    all_playlist = Playlist.select()
    # assert all_playlist.count()  > 1
    logger.debug(f"all_playlist.count() = {all_playlist.count()}")
    p.delete_instance()


def test_video():
    v = Video.create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
    )
    assert v.title == "test"
    try:
        Video.create(title="test")

    except peewee.IntegrityError:
        assert len(Video.select()) == 1

    v3, created3 = Video.get_or_create(title="test")
    assert v3.title == "test"
    assert created3 is False
    assert len(Video.select()) == 1
    v.my_delete_instance()


def test_delete_series():
    s = Series.create(name="test")
    assert s is not None
    s.my_delete_instance()
    s2 = Series.get_or_none(Series.name == "test")
    assert s2 is None


def test_create_channel_file(test_files):
    target = Path(config["paths"]["working"]) / "test_file_output"

    c = Channel.create(name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;")

    assert c is not None

    for file in test_files:
        # with open(source / file, "rb") as src_file:
        #     f: FileInfo = {"name": file, "size": 100, "data": src_file.read()}

        new_name = target / file
        file_type = get_file_type(file)
        nf1 = File(
            path=new_name.parent,
            filename=new_name,
            file_type=file_type,
            extension="asdf",
            channel=c,
        )
        assert nf1 is not None
        assert nf1.extension == "asdf"

        nf2 = File.get_or_create(
            path=target,
            filename="some other name",
            file_type="poster",
            extension="asdffdsa",
            channel=c,
        )
        assert nf2 is not None
    # assert c.files.count() == len(test_files) + 1
    for f in c.files:
        logger.debug(f"{f.filename}")
    c.my_delete_instance()


def test_add_poster_to_channel(test_image_filename):
    c = Channel.create(name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;")
    logger.debug(f"Channel: {c.name}")
    logger.debug(f"{test_image_filename}")
    c.add_file(test_image_filename)
    assert c.files.count() >= 1
    assert c.poster is not None


@pytest.mark.xfail
def test_add_info_to_channel_from_file(test_files):
    c = Channel.create(
        name="Test Channel", youtube_id="asdfasdf", url="www.youtube.com"
    )
    assert c is not None, "Channel not found"

    f = "harry_mack.info.json"
    for tf in test_files:
        if f in tf.name:
            c.add_file(tf)
            break
    c.add_file(f)

    assert c.info is not None
    assert "info" in c.info.filename
    assert c.files.count() >= 1
    assert c.name == "Test Channel"
    c.name = "Harry Mack Channel"
    c.save()
    assert c.name == "Harry Mack Channel"
    c.load_from_info_file()
    assert c.name == "Test Channel"


@pytest.mark.xfail
def test_add_info_from_file_to_playlist_in_db(test_files):
    logger.debug("Test Add Info From File to Playlist 🐣🐣🐣 init")
    playlist_title = "Wordplay Wednesday"
    playlist_id = "PLtbrIhAJmrPAGLnngi0ZOTvNmuNt5uHJk"
    p, created = Playlist.get_or_create(title=playlist_title)
    assert created is False
    assert p is not None
    assert p.youtube_id == playlist_id

    for tf in test_files:
        if (playlist_id in tf.name) and (".info.json" in tf.name):
            p.add_file(tf)
            break
    assert p.info is not None
    assert "info" in p.info.filename
    assert p.files.count() >= 1
    assert p.title == playlist_title
    p.title = "Testing..."
    p.save()
    assert p.title != playlist_title
    p.load_from_info_file()
    assert p.playlist_count == 124
    assert p.title == playlist_title
    logger.debug("Test Add Info From File to Playlist 🐣🐣🐣 finished")


def test_add_poster_to_playlist(test_image_filename):
    p = Playlist.create(title="test")
    logger.debug(f"Playlist: {p.title}")
    logger.debug(f"{test_image_filename}")
    p.add_file(filename=test_image_filename)
    assert p.files.count() >= 1
    assert p.poster is not None


@pytest.mark.xfail
def test_add_poster_to_video(test_image_filename):
    v = Video.create(youtube_id="asdfasdfewr", title="test")
    logger.debug(f"Video: {v.title}")
    logger.debug(f"{test_image_filename}")
    v.add_file(filename=test_image_filename, youtube_id="asdfasdfewr")
    assert v.files.count() >= 1
    assert v.poster is not None


@pytest.mark.xfail
def test_add_file(test_video_filename):
    vid = Video.create(youtube_id="asdfasdfewr")
    vid.add_file(filename=test_video_filename, youtube_id="asdfasdfewr")

    assert vid is not None
    assert vid.files.count() == 1


def test_add_file_to_series(test_image_filename):
    s = Series.create(name="test")
    s.add_file(test_image_filename)
    assert s.files.count() == 1
    assert s.poster is not None


# def test_video_breakpoints():
#     v = Video.create(youtube_id="asdfasdf", duration=1000, title="test")
#     assert v.breakpoints.count() == 2
#     v.add_breakpoint(100)
#     assert v.breakpoints.count() == 3
#     v.add_breakpoint(0)
#     assert v.breakpoints.count() == 3
#     v.add_breakpoint(100)
#     assert v.breakpoints.count() == 3
#     v.add_breakpoint(500)
#     assert v.breakpoints.count() == 4
#     v.delete_breakpoint(100)
#     assert v.breakpoints.count() == 3
#     v.delete_breakpoint(500)
#     assert v.breakpoints.count() == 2
#     v.delete_breakpoint(0)
#     assert v.breakpoints.count() == 2
#     v.delete_breakpoint(1000)
#     assert v.breakpoints.count() == 2


def test_todo_table():
    t1 = TodoTable.create(text="Learn Solara", done=True)
    t2 = TodoTable.create(text="Write cool apps", done=False)
    t3 = TodoTable.create(text="Relax", done=False)
    assert TodoTable.select().count() == 3
    t1.my_delete_instance()
    t2.my_delete_instance()
    t3.my_delete_instance()
    assert TodoTable.select().count() == 0
