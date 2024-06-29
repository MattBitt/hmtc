from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4

from loguru import logger

from hmtc.models import Section as SectionTable

####
### section manager class should be the one that knows about the "type"


@dataclass(frozen=True, order=True)
class Section:
    id: int
    start: int
    end: int
    video_id: int
    section_type: str = "INITIAL"

    def check_times(self) -> None:
        if self.start > self.end:
            raise ValueError("Start time must be less than end time")
        if self.start < 0:
            raise ValueError("Start time must be equal/greater than 0")
        if self.end <= 0:
            raise ValueError("End time must be greater than 0")
        if self.end - self.start <= 0:
            raise ValueError("Section must have a duration greater than 0")

    def __post_init__(self) -> None:
        try:
            self.check_times()
            logger.debug(f"End of Section {self} __post_init__")
        except ValueError as e:
            logger.error(e)
            raise

    def __str__(self) -> str:
        return f"Section {self.id}: {self.start} - {self.end} - {self.section_type}"

    def __repr__(self) -> str:
        return f"Section {self.id}: {self.start} - {self.end} - {self.section_type}"

    @staticmethod
    def get_all():
        return SectionTable.select()


@dataclass
class SectionManager:
    ALLOWED_TYPES = ["intro", "instrumental", "acapella", "outro", "INITIAL"]
    duration: int
    video_id: int = 1  # probably shouldn't be a default
    _sections: Section = field(init=False, default_factory=list)
    section_types: Optional[List[str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.section_types:
            self.section_types = self.ALLOWED_TYPES

        if self.duration <= 0:
            logger.error("Duration must be greater than 0")
            raise ValueError("Duration must be greater than 0")

    @staticmethod
    def from_video(video) -> "SectionManager":
        sm = SectionManager(video_id=video.id, duration=video.duration)
        sm._sections = list(
            SectionTable.select().where(SectionTable.video_id == video.id)
        )
        return sm

    @staticmethod
    def load_sections2(video_id: int) -> List[Section]:
        logger.debug("In load_sections of SectionManager")
        return list(SectionTable.select().where(SectionTable.video_id == video_id))

    @property
    def sections(self):
        return self._sections

    def save_to_db(self, section) -> None:
        SectionTable.create(
            start=section.start,
            end=section.end,
            section_type=section.section_type,
            video_id=self.video_id,
        )

    @staticmethod
    def delete_from_db(section) -> None:
        SectionTable.delete().where(SectionTable.id == section.id).execute()

    @staticmethod
    def get_new_id() -> int:
        return uuid4().int

    @staticmethod
    def get_sections_with_spaces(video):
        sm = SectionManager.from_video(video)
        sections = sm.sections
        timespan = []
        for sect in sections:
            timespan.append([sect.start, sect.end])

        logger.debug(f"Timespan: {timespan}")
        return timespan

    def create_section(self, start: int, end: int, section_type: str) -> None:
        logger.debug("Using instance of SectionManager (self) - create_section")
        if end > self.duration:
            raise ValueError("End time must be less than duration")

        if section_type not in self.section_types:
            raise ValueError("Invalid section type")
        logger.debug(f"Creating section from args {start} {end} {section_type}")
        section = Section(
            id=self.get_new_id(),
            section_type=section_type,
            start=start,
            end=end,
            video_id=self.video_id,
        )
        self.save_to_db(section)
        self._sections.append(section)
        return section

    def add_section(self, section: Section) -> None:
        logger.error("Using instance of SectionManager (self) - add_section")
        self._sections.append(section)

    def remove_section(self, section: Section) -> None:
        logger.error("Using instance of SectionManager (self) - remove_section")
        self._sections.remove(section)

    def split_section_at(self, timestamp: int) -> None:
        logger.error("Using instance of SectionManager (self) - split_section_at")
        for section in self._sections:
            if section.start < timestamp < section.end:
                s1 = self.create_section(
                    start=section.start,
                    end=timestamp,
                    section_type=section.section_type,
                )

                s2 = self.create_section(
                    start=timestamp,
                    end=section.end,
                    section_type=section.section_type,
                )
                self.add_section(s1)
                self.add_section(s2)
                self.remove_section(section)

    def grab_all_sections(self):
        return SectionTable.select()
