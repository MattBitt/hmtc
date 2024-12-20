from pathlib import Path

import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import Channel as ChannelModel
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFile as VideoFileModel


def test_create_video_file(video_item, video_dict):
    assert video_item.id > 0
    assert video_item.title == video_dict["title"]
    video_file = VideoFileModel.create(
        name="test.txt", size=1000, filetype="a text", item_id=video_item.id
    )
    assert video_file.id > 0
    video_file.delete_instance()


@pytest.mark.skip(reason="Not implemented correctly yet. About to do channels.")
def test_video_add_file(video_item, text_file):

    Video.add_file(video_item, text_file)
    _vid = Video.load(video_item.id)
    assert len(_vid.files) == 1
    assert _vid.files[0].name == str(text_file.name)
    assert _vid.files[0].size == 25  # based on the text file content above
    assert _vid.files[0].filetype == "info"
    _vid.files[0].delete_instance()


# start here for testing with tmp_path
# https://pytest-with-eric.com/pytest-best-practices/pytest-tmp-path/
