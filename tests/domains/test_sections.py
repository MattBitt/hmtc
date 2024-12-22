import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel


def test_section_create_and_load(section_dicts, video_item):
    # setup
    sd = section_dicts[0]
    sd["video_id"] = video_item.instance.id
    created_section = Section.create(sd)

    # test
    assert created_section.instance.start == sd["start"]
    assert created_section.instance.id > 0

    loaded_section = Section.load(created_section.instance.id)
    assert loaded_section.instance.start == sd["start"]
    # teardown
    created_section.delete()


def test_section_create_no_start(section_dicts):
    sd = section_dicts[0]
    del sd["start"]
    try:
        Section.create(sd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(section_item):
    loaded_section = Section.get_by(id=section_item.instance.id)
    assert loaded_section.instance.start == section_item.instance.start


def test_get_by_start(section_item):
    loaded_section = Section.get_by(start=section_item.instance.start)
    assert loaded_section.instance.start == section_item.instance.start


def test_select_where(section_item):
    section_query = Section.select_where(start=section_item.instance.start)
    assert len(section_query) == 1
    section = section_query[0]
    assert section.instance.start == section_item.instance.start


def test_update_section(section_item):
    section = section_item
    new_section = section.update({"start": 50})
    assert new_section.instance.start == 50

    section_from_db = (
        SectionModel.select().where(SectionModel.id == section.instance.id).get()
    )
    assert section_from_db.start == 50


def test_section_delete(section_item):
    section = section_item
    section.delete()
    s = (
        SectionModel.select()
        .where(SectionModel.id == section_item.instance.id)
        .get_or_none()
    )
    assert s is None


def test_serialize(section_item):
    s = section_item.serialize()
    assert s["start"] == section_item.instance.start


def test_count(section_dicts, video_item):
    sd1 = section_dicts[0]
    sd1["video_id"] = video_item.instance.id
    sd2 = section_dicts[1]
    sd2["video_id"] = video_item.instance.id
    sd3 = section_dicts[2]
    sd3["video_id"] = video_item.instance.id

    assert Section.count() == 0
    Section.create(sd1)
    Section.create(sd2)
    Section.create(sd3)
    assert Section.count() == 3

    for section_dict in section_dicts:
        section = Section.get_by(start=section_dict["start"])
        section.delete()

    assert Section.count() == 0
