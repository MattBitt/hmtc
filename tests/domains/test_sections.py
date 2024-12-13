import pytest

from hmtc.domains.section import Section
from hmtc.models import Section as SectionModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository

testing_section_dict = {
    "id": 807,
    "start": 0,
    "end": 100,
    "section_type": "verse",
}

testing_video_dict = {
    "id": 8014,
    "title": "Some Test Video Title",
    "desc": "Some Test Video Description",
    "url": "https://www.youtube.com/watch?v=123456",
    "youtube_id": "123456",
    "duration": 100,
    "channel_id": "1",
}


def test_empty_section(empty_db):
    c = Section()
    assert type(c.repo) == Repository


def test_section_create_and_load(seeded_db):
    video = VideoModel.select().first()
    testing_section_dict["video_id"] = video.id
    created_section = Section.create(testing_section_dict)
    assert created_section.start == testing_section_dict["start"]

    assert created_section.id > 0

    loaded_section = Section.load(created_section.id)
    assert loaded_section.start == testing_section_dict["start"]
    assert loaded_section.id == created_section.id

    Section.delete_id(created_section.id)


def test_section_delete(seeded_db):
    video = VideoModel.select().first()
    testing_section_dict["video_id"] = video.id
    new_section = Section.create(testing_section_dict)
    Section.delete_id(new_section.id)
    c = SectionModel.select().where(SectionModel.id == new_section.id).get_or_none()
    assert c is None


def test_serialize(seeded_db):
    _sect = SectionModel.select().first()
    section = Section.serialize(_sect.id)
    assert section["start"] == _sect.start
    assert section["end"] == _sect.end
    assert section["id"] == _sect.id
    assert section["video"]["title"] == _sect.video.title


def test_get_all(seeded_db):
    all_sections = Section.get_all()
    assert len(list(all_sections)) == 5


def test_update_sections(seeded_db):
    SECTION_ID = 1
    section = Section.load(SECTION_ID)
    orig_start = section.start
    assert section.start == 0
    Section.update({"start": 10, "id": 1})
    assert SectionModel.get_by_id(SECTION_ID).start == 10
    Section.update({"start": orig_start, "id": SECTION_ID})
    assert SectionModel.get_by_id(SECTION_ID).start == orig_start
