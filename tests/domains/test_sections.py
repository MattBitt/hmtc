import pytest
from loguru import logger

from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


def test_empty_section(empty_db):
    c = Section()
    assert type(c.repo) == Repository


def test_section_create_and_load(seeded_db, section_dict, video_item):
    section_dict["_video"] = video_item.my_dict()
    created_section = Section.create(section_dict)

    assert created_section.start == section_dict["start"]

    assert created_section.id > 0

    loaded_section = Section.load(created_section.id)
    assert loaded_section.start == section_dict["start"]
    assert loaded_section.id == created_section.id

    Section.delete_id(created_section.id)


def test_section_delete(seeded_db, section_dict, video_item):
    section_dict["_video"] = video_item.my_dict()

    new_section = Section.create(section_dict)

    Section.delete_id(new_section.id)
    c = SectionModel.select().where(SectionModel.id == new_section.id).get_or_none()
    assert c is None


def test_serialize(seeded_db, section_dict, video_item):
    section_dict["_video"] = video_item.my_dict()

    _sect = Section.create(section_dict)

    section = Section.serialize(_sect.id)
    assert section["start"] == _sect.start
    assert section["end"] == _sect.end
    assert section["id"] == _sect.id
    assert section["video"]["title"] == _sect.video.title

    Section.delete_id(_sect.id)


def test_get_all(seeded_db):
    all_sections = Section.get_all()
    assert len(list(all_sections)) == 0


def test_update_sections(seeded_db, section_dict, video_item):
    section_dict["_video"] = video_item.my_dict()

    _sect = Section.create(section_dict)
    orig_start = _sect.start
    Section.update({"start": 10, "id": _sect.id})
    assert SectionModel.get_by_id(_sect).start == 10
    Section.update({"start": orig_start, "id": _sect})
    assert SectionModel.get_by_id(_sect).start == orig_start
