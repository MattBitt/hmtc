import pytest
from hmtc.domains.video import Video
from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.superchat_segment import SuperchatSegment
from hmtc.models import Section as SectionModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.repos.base_repo import Repository

testing_superchat_segment_dict = {
    "start_time_ms": 0,
    "end_time_ms": 2000,
    "next_segment_id": None,
}
testing_section_dict = {
    "start": 0,
    "end": 100,
    "section_type": "verse",
}
testing_video_dict = {
    "title": "Some Test Video Title",
    "description": "Some Test Video Description",
    "url": "https://www.youtube.com/watch?v=123456",
    "youtube_id": "123456",
    "duration": 100,
    "upload_date": "2021-01-01",
}

testing_channel_dict = {
    "title": "Another Test Channel Title (this one in superchat segments)",
    "url": "https://www.youtube.com/channel/1234vzcxvadsf",
    "youtube_id": "1234adfaewr345546542",
    "auto_update": True,
    "last_update_completed": "2021-01-01 00:00:00",
}


def test_empty_superchat_segment():
    c = SuperchatSegment()
    assert type(c.repo) == Repository


def test_superchat_segment_create_and_load(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)
    testing_superchat_segment_dict["section"] = section.my_dict()
    created_superchat_segment = SuperchatSegment.create(testing_superchat_segment_dict)
    assert (
        created_superchat_segment.start_time_ms
        == testing_superchat_segment_dict["start_time_ms"]
    )
    assert (
        created_superchat_segment.end_time_ms
        == testing_superchat_segment_dict["end_time_ms"]
    )
    assert created_superchat_segment.id > 0
    SuperchatSegment.delete_id(created_superchat_segment.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_superchat_segment_delete(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)
    testing_superchat_segment_dict["section"] = section.my_dict()
    created_superchat_segment = SuperchatSegment.create(testing_superchat_segment_dict)
    assert created_superchat_segment.id > 0
    SuperchatSegment.delete_id(created_superchat_segment.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_serialize(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)
    testing_superchat_segment_dict["section"] = section.my_dict()
    _superchat_segment = SuperchatSegment.create(testing_superchat_segment_dict)
    superchat_segment = SuperchatSegment.serialize(_superchat_segment.id)

    assert superchat_segment["start_time_ms"] == _superchat_segment.start_time_ms
    assert superchat_segment["end_time_ms"] == _superchat_segment.end_time_ms
    assert superchat_segment["id"] == _superchat_segment.id
    assert superchat_segment["section"]["id"] == _superchat_segment.section.id
    SuperchatSegment.delete_id(_superchat_segment.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_get_all(seeded_db):
    all_superchat_segments = SuperchatSegment.get_all()
    assert len(list(all_superchat_segments)) == 0


def test_update_superchat_segments(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)
    testing_superchat_segment_dict["section"] = section.my_dict()
    superchat_segment = SuperchatSegment.create(testing_superchat_segment_dict)
    orig_end_time_ms = superchat_segment.end_time_ms
    assert superchat_segment.end_time_ms == 2000
    SuperchatSegment.update({"end_time_ms": 2200, "id": superchat_segment.id})
    assert SuperchatSegmentModel.get_by_id(superchat_segment.id).end_time_ms == 2200
    SuperchatSegment.update(
        {"end_time_ms": orig_end_time_ms, "id": superchat_segment.id}
    )
    assert (
        SuperchatSegmentModel.get_by_id(superchat_segment.id).end_time_ms
        == orig_end_time_ms
    )
    SuperchatSegment.delete_id(superchat_segment.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)
