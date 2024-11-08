from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

import peewee
from loguru import logger

from hmtc.models import File as FileTable
from hmtc.models import (
    Section as SectionTable,
)
from hmtc.models import (
    SectionTopics as SectionTopicsTable,
)
from hmtc.models import (
    Topic as TopicTable,
)
from hmtc.models import (
    Track as TrackTable,
)
from hmtc.schemas.topic import Topic as TopicItem


def create_hms_dict(seconds):
    # moved this from models.py to schemas/section.py
    # 11/7/24 - this is used in the sections page to display
    # label (seconds in milliseconds)

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return dict(
        hour=h,
        minute=m,
        second=s,
    )


@dataclass(frozen=True, order=True)
class Section:
    start: int
    end: int
    video_id: int
    id: int = None
    section_type: str = "INITIAL"
    topics: list = field(default_factory=list)

    def from_model(section: SectionTable) -> "Section":
        return Section(
            id=section.id,
            start=section.start,
            end=section.end,
            video_id=section.video_id,
            section_type=section.section_type,
            topics=[x.topic for x in section.topics],
        )

    def serialize(self) -> dict:

        return {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "start_dict": create_hms_dict(self.start / 1000),
            "end_dict": create_hms_dict(self.end / 1000),
            "start_string": str(timedelta(seconds=self.start / 1000)),
            "end_string": str(timedelta(seconds=self.end / 1000)),
            "video_id": self.video_id,
            "section_type": self.section_type,
            "topics": [TopicItem.from_model(x).serialize() for x in self.topics],
        }

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
            # logger.debug(f"End of Section {self} __post_init__")
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
        logger.debug("Using staticmethod from_video in Section'Table'")
        # query = (
        #     SectionTable.select()
        #     .where(SectionTable.video_id == video.id)
        #     .order_by(SectionTable.start)
        # )
        # results = list(query)
        # if results:
        #     logger.debug(f"Results: {results}")
        # else:
        #     logger.debug("No results found")

        # return results

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

    @staticmethod
    def get_details_for_section(section_id):
        query = (
            SectionTable.select(SectionTable, TopicTable, SectionTopicsTable)
            .join(
                SectionTopicsTable,
                on=(SectionTable.id == SectionTopicsTable.section_id),
                join_type=peewee.JOIN.LEFT_OUTER,
            )
            .join(
                TopicTable,
                join_type=peewee.JOIN.LEFT_OUTER,
            )
            .where(SectionTable.id == section_id)
        ).get()
        if query:
            return query.model_to_dict()


@dataclass
class SectionManager:
    ALLOWED_TYPES = [
        "intro",
        "instrumental",
        "acapella",
        "outro",
        "INITIAL",
        "track",
        "advert",
    ]
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
            SectionTable.select(SectionTable.id, SectionTable.start, SectionTable.end)
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
        logger.debug("🧪🧪🧪🧪 Is this is being used? delete_from_db 9/13/24 🧪🧪🧪🧪")
        SectionTable.delete().where(SectionTable.id == section.id).execute()

    @staticmethod
    def get_by_id(id):
        logger.debug(
            "🧪🧪🧪🧪 get_by_id Is this is being used? get_by_id 9/13/24🧪🧪🧪🧪"
        )
        return SectionTable.get_or_none(SectionTable.id == id)

    @staticmethod
    def get_section_details(id):
        # 10/28/24 - adding Track object and files to the query
        query = (
            SectionTable.select(
                SectionTable, TopicTable, SectionTopicsTable, TrackTable, FileTable
            )
            .join(
                SectionTopicsTable,
                on=(SectionTable.id == SectionTopicsTable.section_id),
                join_type=peewee.JOIN.LEFT_OUTER,
            )
            .join(
                TopicTable,
                join_type=peewee.JOIN.LEFT_OUTER,
            )
            .switch(SectionTable)
            .join(
                TrackTable,
                peewee.JOIN.LEFT_OUTER,
                on=(SectionTable.track_id == TrackTable.id),
            )
            .join(
                FileTable,
                peewee.JOIN.LEFT_OUTER,
                on=(TrackTable.id == FileTable.track_id),
            )
            .where(SectionTable.id == id)
        ).get_or_none()
        # logger.debug(f"Query Result: {query}")
        if query:
            return Section.from_model(query).serialize()
        else:
            return None
