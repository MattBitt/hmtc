import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.superchat_segment import SuperchatSegment
from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.repos.base_repo import Repository


def test_empty_superchat_segment():
    c = SuperchatSegment()
    assert type(c.repo) == Repository


def test_superchat_segment_create_and_load(
    seeded_db, section_dict, superchat_segment_dict, video_item
):

    section_dict["_video"] = video_item.my_dict()
    section = Section.create(section_dict)
    superchat_segment_dict["section"] = section.my_dict()
    created_superchat_segment = SuperchatSegment.create(superchat_segment_dict)
    assert (
        created_superchat_segment.start_time_ms
        == superchat_segment_dict["start_time_ms"]
    )
    assert (
        created_superchat_segment.end_time_ms == superchat_segment_dict["end_time_ms"]
    )
    assert created_superchat_segment.id > 0
    SuperchatSegment.delete_id(created_superchat_segment.id)
    Section.delete_id(section.id)


def test_superchat_segment_delete(
    seeded_db, section_dict, superchat_segment_dict, video_item
):
    section_dict["_video"] = video_item.my_dict()
    section = Section.create(section_dict)
    superchat_segment_dict["section"] = section.my_dict()
    created_superchat_segment = SuperchatSegment.create(superchat_segment_dict)
    assert created_superchat_segment.id > 0
    SuperchatSegment.delete_id(created_superchat_segment.id)
    Section.delete_id(section.id)


def test_serialize(seeded_db, section_dict, superchat_segment_dict, video_item):
    section_dict["_video"] = video_item.my_dict()
    section = Section.create(section_dict)
    superchat_segment_dict["section"] = section.my_dict()
    _superchat_segment = SuperchatSegment.create(superchat_segment_dict)
    superchat_segment = SuperchatSegment.serialize(_superchat_segment.id)

    assert superchat_segment["start_time_ms"] == _superchat_segment.start_time_ms
    assert superchat_segment["end_time_ms"] == _superchat_segment.end_time_ms
    assert superchat_segment["id"] == _superchat_segment.id
    assert superchat_segment["section"]["id"] == _superchat_segment.section.id
    SuperchatSegment.delete_id(_superchat_segment.id)
    Section.delete_id(section.id)


def test_get_all(seeded_db):
    all_superchat_segments = SuperchatSegment.get_all()
    assert len(list(all_superchat_segments)) == 0


def test_update_superchat_segments(
    seeded_db, section_dict, superchat_segment_dict, video_item
):
    section_dict["_video"] = video_item.my_dict()
    section = Section.create(section_dict)
    superchat_segment_dict["section"] = section.my_dict()
    _superchat_segment = SuperchatSegment.create(superchat_segment_dict)
    orig_end_time_ms = _superchat_segment.end_time_ms
    assert _superchat_segment.end_time_ms == 10
    SuperchatSegment.update({"end_time_ms": 2200, "id": _superchat_segment.id})
    assert SuperchatSegmentModel.get_by_id(_superchat_segment.id).end_time_ms == 2200
    SuperchatSegment.update(
        {"end_time_ms": orig_end_time_ms, "id": _superchat_segment.id}
    )
    assert (
        SuperchatSegmentModel.get_by_id(_superchat_segment.id).end_time_ms
        == orig_end_time_ms
    )
    SuperchatSegment.delete_id(_superchat_segment.id)
    Section.delete_id(section.id)
