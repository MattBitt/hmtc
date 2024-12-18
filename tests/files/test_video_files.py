from pathlib import Path

import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import Channel as ChannelModel
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFile as VideoFileModel

testing_video_dict = {
    "description": "This is only for testing.in the files tab.",
    "duration": 400,
    "title": "Another quirky title to stand out.",
    "unique_content": True,
    "upload_date": "2021-01-01",
    "url": "https://www.youtube.com/watch?v=1234vzcxvadsf",
    "youtube_id": "vjhfadsklfhew",
}


@pytest.fixture(scope="function")
def video_item(seeded_db):
    channel = ChannelModel(
        title="Test Channel",
        youtube_id="1234q2w43asdf",
        url="https://www.youtube.com/channel/1234",
    )
    channel.save()
    testing_video_dict["_channel"] = channel.my_dict()

    created_video = Video.create(testing_video_dict)
    yield Video.load(created_video.id)
    Video.delete_id(created_video.id)
    Channel.delete_id(channel.id)


def test_create_video_file(video_item):
    assert video_item.id > 0
    assert video_item.title == testing_video_dict["title"]
    video_file = VideoFileModel.create(
        name="test.txt", size=1000, filetype="a text", item_id=video_item.id
    )
    assert video_file.id > 0
    video_file.delete_instance()


def test_video_add_file(video_item):
    example_file = dict(name=Path("test.txt"), size=1000, filetype="a text")
    Video.add_file(video_item, example_file)
    _vid = Video.load(video_item.id)
    assert len(_vid.files) == 1
    assert _vid.files[0].name == str(example_file["name"])
    _vid.files[0].delete_instance()
