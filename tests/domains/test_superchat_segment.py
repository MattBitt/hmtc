import pytest

from hmtc.domains.section import Section
from hmtc.domains.superchat_segment import SuperchatSegment
from hmtc.models import SuperchatSegment as SuperchatSegmentModel


def test_superchatsegment_create_and_load(superchat_segment_dicts, section_item):
    # setup
    sd = superchat_segment_dicts[0]
    sd["section_id"] = section_item.instance.id
    created_superchatsegment = SuperchatSegment.create(sd)

    # test
    assert created_superchatsegment.instance.start_time_ms == sd["start_time_ms"]
    assert created_superchatsegment.instance.id > 0

    loaded_superchatsegment = SuperchatSegment.load(
        created_superchatsegment.instance.id
    )
    assert loaded_superchatsegment.instance.start_time_ms == sd["start_time_ms"]
    # teardown
    created_superchatsegment.delete()


def test_superchatsegment_create_no_start_time(superchat_segment_dicts):
    sd = superchat_segment_dicts[0]
    del sd["start_time_ms"]
    try:
        SuperchatSegment.create(sd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(superchat_segment_item):
    loaded_superchat_segment = SuperchatSegment.get_by(
        id=superchat_segment_item.instance.id
    )
    assert (
        loaded_superchat_segment.instance.start_time_ms
        == superchat_segment_item.instance.start_time_ms
    )


def test_get_by_start_time(superchat_segment_item):
    loaded_superchat_segment = SuperchatSegment.get_by(
        start_time_ms=superchat_segment_item.instance.start_time_ms
    )
    assert (
        loaded_superchat_segment.instance.start_time_ms
        == superchat_segment_item.instance.start_time_ms
    )


def test_select_where(superchat_segment_item):
    superchatsegment_query = SuperchatSegment.select_where(
        start_time_ms=superchat_segment_item.instance.start_time_ms
    )
    assert len(superchatsegment_query) == 1
    superchatsegment = superchatsegment_query[0]
    assert (
        superchatsegment.instance.start_time_ms
        == superchat_segment_item.instance.start_time_ms
    )


def test_update_superchatsegment(superchat_segment_item):
    superchatsegment = superchat_segment_item
    new_superchatsegment = superchatsegment.update({"start_time_ms": 1000})
    assert new_superchatsegment.instance.start_time_ms == 1000

    superchatsegment_from_db = (
        SuperchatSegmentModel.select()
        .where(SuperchatSegmentModel.id == superchatsegment.instance.id)
        .get()
    )
    assert superchatsegment_from_db.start_time_ms == 1000


def test_superchatsegment_delete(superchat_segment_item):
    superchatsegment = superchat_segment_item
    superchatsegment.delete()
    s = (
        SuperchatSegmentModel.select()
        .where(SuperchatSegmentModel.id == superchat_segment_item.instance.id)
        .get_or_none()
    )
    assert s is None


def test_serialize(superchat_segment_item):
    s = superchat_segment_item.serialize()
    assert s["start_time_ms"] == superchat_segment_item.instance.start_time_ms


def test_count(superchat_segment_dicts, section_item):
    sd1 = superchat_segment_dicts[0]
    sd1["section_id"] = section_item.instance.id
    sd2 = superchat_segment_dicts[1]
    sd2["section_id"] = section_item.instance.id
    sd3 = superchat_segment_dicts[2]
    sd3["section_id"] = section_item.instance.id

    assert SuperchatSegment.count() == 0
    SuperchatSegment.create(sd1)
    SuperchatSegment.create(sd2)
    SuperchatSegment.create(sd3)
    assert SuperchatSegment.count() == 3

    for superchat_segment_dict in superchat_segment_dicts:
        superchatsegment = SuperchatSegment.get_by(
            start_time_ms=superchat_segment_dict["start_time_ms"]
        )
        superchatsegment.delete()

    assert SuperchatSegment.count() == 0
