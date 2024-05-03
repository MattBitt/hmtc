import pytest
import peewee
from pathlib import Path
from loguru import logger
from hmtc.models import (
    File,
    Video,
    Series,
    Channel,
    ChannelFile,
    Playlist,
    Track,
    get_file_type,
)
from hmtc.components.file_drop_card import FileInfo
from hmtc.config import init_config


config = init_config()
source = (
    Path(config.get("GENERAL", "BASE_PATH"))
    / config.get("GENERAL", "TESTDATA_PATH")
    / "files"
)


def test_series():
    Series.create_table()
    s, created = Series.get_or_create(
        name="test", start_date="2020-01-01", end_date="2020-12-31"
    )
    assert created is True
    assert s.name == "test"
    try:
        s2 = Series.create(name="test", start_date="2020-01-01", end_date="2020-12-31")
    except peewee.IntegrityError as e:
        assert len(Series.select()) == 1
    s3, created = Series.get_or_create(name="test")
    assert s3.name == "test"
    assert len(Series.select()) == 1
    s.delete_instance()


# this test leaves a record in the database
def test_permanance_setup():
    s = Series.create(name="test")
    assert s is not None


def test_permanance_execute():
    s = Series.get_or_none(Series.name == "test")
    assert s is None


def test_channel():
    Channel.create_table()
    c, created = Channel.get_or_create(
        name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;"
    )
    assert c.name == "test"
    assert created is True
    try:
        c2 = Channel.create(name="test", url="www.yahoo.com")
    except peewee.IntegrityError as e:
        assert len(Channel.select()) == 1
    c3, created = Channel.get_or_create(name="test", url="www.yahoo.com")
    assert c3.name == "test"
    assert created is False
    assert len(Channel.select()) == 1
    c.delete_instance()


def test_playlist():
    Playlist.create_table()
    p, created = Playlist.get_or_create(
        name="test", url="www.yahoo.com/playlists", youtube_id="PLTvadsfadghas"
    )
    assert created is True
    assert p.name == "test"
    try:
        Playlist.create(name="test")

    except peewee.IntegrityError as e:

        assert len(Playlist.select()) == 1

    p3, created3 = Playlist.get_or_create(name="test")
    assert p3.name == "test"
    assert created3 is False
    assert len(Playlist.select()) == 1
    p.delete_instance()


def test_video():
    Video.create_table()
    v, created = Video.get_or_create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
        file_path="",
        # channel=Channel.get_or_create(
        #     name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;"
        # ),
        # playlist=Playlist.get_or_create(
        #     name="test", url="www.yahoo.com/playlists", youtube_id="PLTvadsfadghas"
        # ),
    )
    assert created is True
    assert v.title == "test"
    try:
        Video.create(title="test")

    except peewee.IntegrityError as e:

        assert len(Video.select()) == 1

    v3, created3 = Video.get_or_create(title="test")
    assert v3.title == "test"
    assert created3 is False
    assert len(Video.select()) == 1
    v.delete_instance()


def test_delete_series():
    s = Series.create(name="test")
    assert s is not None
    s.delete_instance()
    s2 = Series.get_or_none(Series.name == "test")
    assert s2 is not None
    assert s2.name == "test"
    assert s2.deleted_at is not None


# def test_create_new_file(test_files):
#     target = Path(config.get("GENERAL", "BASE_PATH")) / "temp"
#     if target.exists():
#         for file in target.glob("*"):
#             file.unlink()
#         target.rmdir()

#     target.mkdir()

#     for file in test_files:
#         # pretend this is the uploaded file object
#         with open(source / file, "rb") as src_file:
#             f: FileInfo = {"name": file, "size": 100, "data": src_file.read()}

#         new_name = target / file

#         cf = ChannelFile(target=target, new_name=new_name, file_type=f)
#         assert cf is not None


def test_create_channel_file(test_files):
    target = Path(config.get("GENERAL", "BASE_PATH")) / "temp"

    c = Channel.create(name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;")

    assert c is not None

    for file in test_files:
        # with open(source / file, "rb") as src_file:
        #     f: FileInfo = {"name": file, "size": 100, "data": src_file.read()}

        new_name = target / file
        file_type = get_file_type(file)
        nf1 = ChannelFile(
            path=new_name.parent,
            filename=new_name,
            file_type=file_type,
            extension="asdf",
            channel=c,
        )
        assert nf1 is not None
        assert nf1.extension == "asdf"

        nf2 = ChannelFile.get_or_create(
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
    c.delete_instance()
