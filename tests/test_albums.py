from pathlib import Path

import pytest
from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.models import File as FileModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import FileManager


def test_create_album():
    album = AlbumModel.create(title="Test Album", release_date="2021-01-01")
    assert album.title == "Test Album"
    assert album.release_date == "2021-01-01"


def test_album_item():
    album = AlbumModel.create(title="Test Album", release_date="2021-01-01")
    album_item = AlbumItem.from_model(album)
    assert album_item.title == "Test Album"
    assert album_item.release_date == "2021-01-01"


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
    # this should be 2 if i'm renumbering
    assert album.tracks[1].track_number == 3
    logger.error(album.tracks)


@pytest.mark.skip
def test_add_poster(test_image_filename):

    album = AlbumModel.create(title="test")

    album_item = AlbumItem.from_model(album)

    album_poster = FileManager.add_path_to_album(path=test_image_filename, album=album)

    file_to_check = FileModel.select().where(FileModel.album_id == album.id).get()
    assert "cover" in file_to_check.filename

    logger.error(album_poster)


def test_use_video_poster(test_image_filename):
    new_video = VideoModel.create(
        title="Test Video",
        description="This is a test video",
        youtube_id="12345678",
        upload_date="2021-01-01",
        duration=1200,
    )
    FileManager.add_path_to_video(path=test_image_filename, video=new_video)

    album = AlbumModel.create(title="test19")

    new_video.album_id = album.id
    new_video.save()

    album_item = AlbumItem.from_model(album)
    album_item.use_video_poster()

    file_to_check = FileModel.select().where(FileModel.album_id == album.id).get()
    # this should fail if the file has been renamed
    assert "cover" in file_to_check.filename
    assert (Path(file_to_check.path) / file_to_check.filename).exists()
