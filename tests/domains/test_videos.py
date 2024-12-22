import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import Video as VideoModel


@pytest.fixture
def channel_item(channel_dicts):
    channel = Channel.create(channel_dicts[0])
    yield channel
    channel.delete()


@pytest.fixture
def video_item(video_dicts, channel_item):
    vd = video_dicts[0]
    vd["channel_id"] = channel_item.instance.id
    created_video = Video.create(vd)
    yield created_video
    created_video.delete()


def test_video_create_and_load(video_dicts, channel_item):
    # setup
    vd = video_dicts[0]
    vd["channel_id"] = channel_item.instance.id
    created_video = Video.create(vd)

    # test
    assert created_video.instance.title == vd["title"]
    assert created_video.instance.id > 0

    loaded_video = Video.load(created_video.instance.id)
    assert loaded_video.instance.title == vd["title"]
    # teardown
    created_video.delete()


def test_video_create_no_title(video_dicts):
    vd = video_dicts[0]
    del vd["title"]
    try:
        Video.create(vd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(video_item):
    loaded_video = Video.get_by(id=video_item.instance.id)
    assert loaded_video.instance.title == video_item.instance.title


def test_get_by_title(video_item):
    loaded_video = Video.get_by(title=video_item.instance.title)
    assert loaded_video.instance.title == video_item.instance.title


def test_select_where(video_item):
    video_query = Video.select_where(title=video_item.instance.title)
    assert len(video_query) == 1
    video = video_query[0]
    assert video.instance.title == video_item.instance.title


def test_update_video(video_item):
    video = video_item
    new_video = video.update({"title": "New Title"})
    assert new_video.instance.title == "New Title"

    video_from_db = VideoModel.select().where(VideoModel.id == video.instance.id).get()
    assert video_from_db.title == "New Title"


def test_video_delete(video_item):
    video = video_item
    video.delete()
    v = VideoModel.select().where(VideoModel.id == video_item.instance.id).get_or_none()
    assert v is None


def test_serialize(video_item):
    s = video_item.serialize()
    assert s["title"] == video_item.instance.title


def test_count(video_dicts, channel_item):
    vd1 = video_dicts[0]
    vd1["channel_id"] = channel_item.instance.id
    vd2 = video_dicts[1]
    vd2["channel_id"] = channel_item.instance.id
    vd3 = video_dicts[2]
    vd3["channel_id"] = channel_item.instance.id

    assert Video.count() == 0
    Video.create(vd1)
    Video.create(vd2)
    Video.create(vd3)
    assert Video.count() == 3

    for video_dict in video_dicts:
        video = Video.get_by(title=video_dict["title"])
        video.delete()

    assert Video.count() == 0
