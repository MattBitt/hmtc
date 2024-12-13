import pytest

from hmtc.domains.superchat_segment import SuperchatSegment
from hmtc.models import Section as SectionModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.repos.base_repo import Repository

testing_superchat_segment_dict = {
    "id": 80945,
    "start_time_ms": 0,
    "end_time_ms": 1000,
    "next_segment_id": None,
}


def test_empty_superchat_segment():
    c = SuperchatSegment()
    assert type(c.repo) == Repository


def test_superchat_segment_create_and_load(seeded_db):
    section = SectionModel.select().first()
    testing_superchat_segment_dict
    testing_superchat_segment_dict["section_id"] = section.id

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

    #     loaded_superchat_segment = SuperchatSegment.load(created_superchat_segment.id)
    #     assert (
    #         loaded_superchat_segment.start_time_ms
    #         == testing_superchat_segment_dict["start_time_ms"]
    #     )
    #     assert (
    #         loaded_superchat_segment.end_time_ms
    #         == testing_superchat_segment_dict["end_time_ms"]
    #     )
    #     assert loaded_superchat_segment.id > 0
    #     assert loaded_superchat_segment.section.id == section.id
    SuperchatSegment.delete_id(created_superchat_segment.id)


def test_superchat_segment_delete(seeded_db):
    section = SectionModel.select().first()
    testing_superchat_segment_dict["section_id"] = section.id
    new_segment = SuperchatSegment.create(testing_superchat_segment_dict)
    assert new_segment.id > 0
    SuperchatSegment.delete_id(new_segment.id)


def test_serialize(seeded_db):
    _superchat_segment = SuperchatSegmentModel.select().first()
    superchat_segment = SuperchatSegment.serialize(_superchat_segment.id)

    assert superchat_segment["start_time_ms"] == _superchat_segment.start_time_ms
    assert superchat_segment["end_time_ms"] == _superchat_segment.end_time_ms
    assert superchat_segment["id"] == _superchat_segment.id
    assert superchat_segment["section"]["id"] == _superchat_segment.section.id


def test_get_all(seeded_db):
    all_superchat_segments = SuperchatSegment.get_all()
    assert len(list(all_superchat_segments)) == 3


def test_update_superchat_segments(seeded_db):
    SUPERCHAT_SEGMENT_ID = 1
    superchat_segment = SuperchatSegment.load(SUPERCHAT_SEGMENT_ID)
    orig_end_time_ms = superchat_segment.end_time_ms
    assert superchat_segment.end_time_ms == 2000
    SuperchatSegment.update({"end_time_ms": 2200, "id": 1})
    assert SuperchatSegmentModel.get_by_id(SUPERCHAT_SEGMENT_ID).end_time_ms == 2200
    SuperchatSegment.update(
        {"end_time_ms": orig_end_time_ms, "id": SUPERCHAT_SEGMENT_ID}
    )
    assert (
        SuperchatSegmentModel.get_by_id(SUPERCHAT_SEGMENT_ID).end_time_ms
        == orig_end_time_ms
    )
