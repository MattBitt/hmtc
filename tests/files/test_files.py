from datetime import datetime

import pytest

from loguru import logger

from hmtc.models import *

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
    info_file.unlink()

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
    track_item.delete
    # cleanup
    # info_file.unlink() # should be deleted by its owner
    assert not info_file.exists()



