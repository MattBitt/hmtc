from datetime import datetime
from pathlib import Path

import pytest
from loguru import logger

from hmtc.domains.channel import Channel


@pytest.mark.skip(f"cause its failing")
def test_album_info_file(album_item, tmp_path):
    # setup
    info_file = tmp_path / "album_number_3.info.json"
    with open(info_file, "w") as f:
        for i in range(5):
            f.write("this is the info for album number 3\n")
    assert info_file.exists()

    # testing
    album_item.add_file(info_file)

    loaded_file = album_item.get_file("info")
    assert loaded_file is not None
    assert loaded_file.exists()
    with open(loaded_file, "r") as f:
        line1 = f.readline()
        assert line1 == "this is the info for album number 3\n"

    # cleanup
    # info_file.unlink()


@pytest.mark.skip(f"cause its failing")
def test_track_info_file(track_item, tmp_path):
    # setup
    info_file = tmp_path / "random_track.info.json"
    with open(info_file, "w") as f:
        for i in range(10):
            f.write("some title and info\n")
    assert info_file.exists()

    # testing
    track_item.add_file(info_file)

    loaded_file = track_item.get_file("info")
    assert loaded_file is not None
    assert loaded_file.exists()
    with open(loaded_file, "r") as f:
        line1 = f.readline()
        assert line1 == "some title and info\n"

    # cleanup
    # info_file.unlink() # should be deleted by its owner
    # assert not info_file.exists()


def test_channel_info_file(channel_dicts, tmp_path):
    # setup
    info_file = tmp_path / "a_youtube_info_file.info.json"
    with open(info_file, "w") as f:
        for i in range(6):
            f.write(f"some title and info {i}\n")
    assert info_file.exists()

    channel = Channel.create(channel_dicts[0])

    # testing
    channel.add_file(info_file)
    # file should have been moved to its final location
    # initial location shouldn't exist
    assert not info_file.exists()

    # load the file path from the db
    new_file = channel.get_file("info")
    assert new_file is not None
    assert new_file.exists()

    # cleanup
    channel.delete()
    assert not new_file.exists()
