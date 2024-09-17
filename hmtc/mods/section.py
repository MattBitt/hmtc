from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4

from loguru import logger

from hmtc.models import Section as SectionTable


@dataclass(frozen=True, order=True)
class Section:
    start: int
    end: int
    video_id: int
    id: int = None
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

    @staticmethod
    def get_by_id(id):
        return SectionTable.get_or_none(SectionTable.id == id)

    @staticmethod
    def from_video(video):
        logger.debug(f"Grabbing sections for video {video.id}")
        query = (
            SectionTable.select()
            .where(SectionTable.video_id == video.id)
            .order_by(SectionTable.start)
        )
        results = list(query)
        if results:
            logger.debug(f"Results: {results}")
        else:
            logger.debug("No results found")

        return results

    @staticmethod
    def get_by_start(video_id, start):
        query = SectionTable.select().where(
            (SectionTable.start == start) & (SectionTable.video_id == video_id)
        )
        return query.get()

    @staticmethod
    def get_by_end(video_id, end):
        query = SectionTable.select().where(
            (SectionTable.end == end) & (SectionTable.video_id == video_id)
        )
        return query.get()


@dataclass
class SectionManager:
    ALLOWED_TYPES = ["intro", "instrumental", "acapella", "outro", "INITIAL", "track"]
    duration: int  # this is in seconds, the section start and end are in milliseconds
    video_id: int = 1  # probably shouldn't be a default
    _sections: Section = field(init=False, default_factory=list)
    section_types: Optional[List[str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.section_types:
            self.section_types = self.ALLOWED_TYPES

        if self.duration <= 0:
            logger.error("Duration must be greater than 0")
            raise ValueError("Duration must be greater than 0")

    ##### definitely used functions (9/13/24)
    @property
    def sections(self):

        return self._sections

    @staticmethod
    def from_video(video) -> "SectionManager":

        sm = SectionManager(video_id=video.id, duration=video.duration)
        sm._sections = list(
            SectionTable.select()
            .where(SectionTable.video_id == video.id)
            .order_by(SectionTable.start)
        )
        return sm

    def save_to_db(self, section) -> None:
        new_sect = SectionTable.create(
            start=section.start,
            end=section.end,
            section_type=section.section_type,
            video_id=self.video_id,
        )
        return new_sect

    def create_section(self, start: int, end: int, section_type: str) -> None:
        logger.debug("Using instance of SectionManager (self) - create_section")
        if end > self.duration:
            raise ValueError("End time must be less than duration")

        if section_type not in self.section_types:
            raise ValueError("Invalid section type")
        logger.debug(f"Creating section from args {start} {end} {section_type}")
        section = Section(
            section_type=section_type,
            start=start * 1000,  # convert to milliseconds
            end=end * 1000,  # convert to milliseconds
            video_id=self.video_id,
        )
        new_sect = self.save_to_db(section)
        self._sections.append(section)
        return new_sect.id

    ##### may not be used functions (9/13/24)
    @staticmethod
    def delete_from_db(section) -> None:
        logger.debug("🧪🧪🧪🧪 Is this is being used? 9/13/24 🧪🧪🧪🧪")
        SectionTable.delete().where(SectionTable.id == section.id).execute()

    @staticmethod
    def get_by_id(id):
        logger.debug("🧪🧪🧪🧪 get_by_id Is this is being used? 9/13/24🧪🧪🧪🧪")
        return SectionTable.get_or_none(SectionTable.id == id)
