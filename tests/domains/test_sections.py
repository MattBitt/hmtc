import pytest

from hmtc.domains.section import Section
from hmtc.models import Section as SectionModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_item,
    channel_item,
    section_dict1,
    section_dict2,
    section_dict3,
    section_item,
    series_item,
    video_item,
    youtube_series_item,
)


def test_empty_section():
    c = Section()
    assert type(c.repo) == Repository


def test_section_create_and_load(section_dict1, video_item):
    section_dict1["video"] = video_item.title
    created_section = Section.create(section_dict1)
    assert created_section.start == section_dict1["start"]

    assert created_section.id > 0

    loaded_section = Section.load(created_section.id)
    assert loaded_section.start == section_dict1["start"]


def test_section_delete(section_item):

    Section.delete_id(section_item.id)
    c = SectionModel.select().where(SectionModel.id == section_item.id).get_or_none()
    assert c is None


def test_serialize(section_item, video_item):
    s = Section.serialize(section_item.id)
    assert s["start"] == section_item.start
    assert s["end"] == section_item.end
    assert s["id"] == section_item.id
    assert s["video"]["title"] == video_item.title


def test_get_all(section_item):
    all_sections = Section.get_all()
    assert len(list(all_sections)) == 1


def test_update_sections(section_item):
    section = Section.load(section_item.id)
    assert section.start == section_item.start
    assert section.end == section_item.end
    Section.update({"start": 15, "id": section_item.id})
    assert SectionModel.get_by_id(section_item.id).start == 15
