import pytest
from loguru import logger
from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository

testing_section_dict = {
    "start": 0,
    "end": 100,
    "section_type": "verse",
}

testing_video_dict = {
    "title": "Some Test Video Title",
    "description": "Some Test Video Description",
    "url": "https://www.youtube.com/watch?v=123456",
    "youtube_id": "12345678910",
    "duration": 100,
    "upload_date": "2021-01-01",
}

testing_channel_dict = {
    "title": "Another Test Channel Title",
    "url": "https://www.youtube.com/channel/1234vzcxvadsf",
    "youtube_id": "1234adfaewr",
    "auto_update": True,
    "last_update_completed": "2021-01-01 00:00:00",
}


def test_empty_section(empty_db):
    c = Section()
    assert type(c.repo) == Repository


def test_section_create_and_load(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()

    created_section = Section.create(testing_section_dict)
    assert created_section.start == testing_section_dict["start"]

    assert created_section.id > 0

    loaded_section = Section.load(created_section.id)
    assert loaded_section.start == testing_section_dict["start"]
    assert loaded_section.id == created_section.id

    Section.delete_id(created_section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_section_delete(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()

    new_section = Section.create(testing_section_dict)
    Section.delete_id(new_section.id)
    c = SectionModel.select().where(SectionModel.id == new_section.id).get_or_none()
    assert c is None

    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_serialize(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    _sect = Section.create(testing_section_dict)

    section = Section.serialize(_sect.id)
    assert section["start"] == _sect.start
    assert section["end"] == _sect.end
    assert section["id"] == _sect.id
    assert section["video"]["title"] == _sect.video.title

    Section.delete_id(_sect.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_get_all(seeded_db):
    all_sections = Section.get_all()
    assert len(list(all_sections)) == 0


def test_update_sections(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    _sect = Section.create(testing_section_dict)
    orig_start = _sect.start
    Section.update({"start": 10, "id": _sect.id})
    assert SectionModel.get_by_id(_sect).start == 10
    Section.update({"start": orig_start, "id": _sect})
    assert SectionModel.get_by_id(_sect).start == orig_start

    Video.delete_id(video.id)
    Channel.delete_id(channel.id)
