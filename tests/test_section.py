from hmtc.mods.section import Section, SectionManager
import pytest
from hmtc.models import Video

# class Video:
#     def __init__(self, id, duration):
#         self.id = id
#         self.duration = duration
#         self.sections = []


# vid = Video(1, 300)


def test_section():
    s = Section(id=1, start=0, end=150, video_id=4)
    assert s.start == 0
    assert s.end == 150
    assert s.video_id == 4


def test_section_comparison():
    s = Section(id=1, start=0, end=150, video_id=4)
    s2 = Section(id=2, start=150, end=300, video_id=4)
    assert s < s2
    assert s2 > s
    s3 = Section(id=3, start=151, end=300, video_id=4)
    assert s3 > s2


@pytest.mark.xfail
def test_section_manager():
    sm = SectionManager(duration=300)
    sections = sm.create_section(start=0, end=300, section_type="acapella")
    assert sections[0].start == 0
    assert sections[0].end == 300
    assert sections[0].section_type == "acapella"


def test_section_manager_from_db(video):

    sm = SectionManager.from_video(video)
    assert sm.duration == 8531
    assert sm.sections == []


def test_section_manager_types():
    sm = SectionManager(duration=300, section_types=["intro"])
    try:
        sm.create_section(start=150, end=300, section_type=["instrumental"])
        assert False
    except ValueError:
        pass


def test_section_validators(video):
    sm = SectionManager.from_video(video)
    assert sm.duration == 8531
    try:
        sm.create_section(start=0, end=0, section_type="intro")
        assert False
    except ValueError:
        pass
    try:
        sm.create_section(start=0, end=10000, section_type="acapella")
        assert False
    except ValueError:
        pass


def test_static_section_manager_sections(video):
    sm = SectionManager.from_video(video)
    assert sm.sections == []
    sm.create_section(start=0, end=300, section_type="intro")
    assert len(sm.sections) == 1


@pytest.mark.xfail
def test_split_sections():
    sm = SectionManager(duration=300)
    sm.create_section(start=0, end=300, section_type="intro")
    assert len(sm.sections) == 1
    sm.split_section_at(150)
    assert len(sm.sections) == 2
    assert sm.sections[0].start == 0
    assert sm.sections[0].end == 150
    sm.split_section_at(200)
    assert len(sm.sections) == 3
