import pytest

from hmtc.domains.superchat_segment import SuperchatSegment
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_item,
    channel_item,
    section_item,
    series_item,
    superchat_segment_dict1,
    superchat_segment_dict2,
    superchat_segment_dict3,
    superchat_segment_item,
    video_item,
    youtube_series_item,
)


def test_empty_superchat_segment():
    c = SuperchatSegment()
    assert type(c.repo) == Repository


def test_superchat_segment_create_and_load(superchat_segment_dict1, section_item):
    superchat_segment_dict1["section_id"] = section_item.id

    created_superchat_segment = SuperchatSegment.create(superchat_segment_dict1)
    assert (
        created_superchat_segment.start_time_ms
        == superchat_segment_dict1["start_time_ms"]
    )
    assert (
        created_superchat_segment.end_time_ms == superchat_segment_dict1["end_time_ms"]
    )
    assert created_superchat_segment.id > 0

    loaded_superchat_segment = SuperchatSegment.load(created_superchat_segment.id)
    assert (
        loaded_superchat_segment.start_time_ms
        == superchat_segment_dict1["start_time_ms"]
    )
    assert (
        loaded_superchat_segment.end_time_ms == superchat_segment_dict1["end_time_ms"]
    )
    assert loaded_superchat_segment.id > 0
    assert loaded_superchat_segment.section.id == section_item.id


def test_superchat_segment_delete(superchat_segment_item):

    SuperchatSegment.delete_id(superchat_segment_item.id)
    c = (
        SuperchatSegmentModel.select()
        .where(SuperchatSegmentModel.id == superchat_segment_item.id)
        .get_or_none()
    )
    assert c is None


def test_serialize(superchat_segment_item, section_item):
    s = SuperchatSegment.serialize(superchat_segment_item.id)
    assert s["start_time_ms"] == superchat_segment_item.start_time_ms
    assert s["end_time_ms"] == superchat_segment_item.end_time_ms
    assert s["id"] == superchat_segment_item.id
    assert s["section"]["id"] == section_item.id


def test_get_all(superchat_segment_item):
    all_superchat_segments = SuperchatSegment.get_all()
    assert len(list(all_superchat_segments)) == 1


def test_update_superchat_segments(superchat_segment_item):
    superchat_segment = SuperchatSegment.load(superchat_segment_item.id)
    assert superchat_segment.start_time_ms == superchat_segment_item.start_time_ms
    SuperchatSegment.update({"start_time_ms": 15, "id": superchat_segment_item.id})
    assert (
        SuperchatSegmentModel.get_by_id(superchat_segment_item.id).start_time_ms == 15
    )
