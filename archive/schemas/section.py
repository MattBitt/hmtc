from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

import peewee
from loguru import logger

from hmtc.models import (
    Section as SectionModel,
)
from hmtc.models import (
    SectionTopics as SectionTopicsModel,
)
from hmtc.models import (
    SuperchatSegment as SuperchatSegmentModel,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import (
    Track as TrackModel,
)
from hmtc.schemas.base import BaseItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat_segment import SuperchatSegment as SuperchatSegmentItem
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


@dataclass(frozen=True, order=True, kw_only=True)
class Section(BaseItem):
    start: int
    end: int

    id: int = None
    section_type: str = "_INITIAL_"
    item_type: str = "SECTION"
    topics: list = field(default_factory=list)
    video_id: int = 0
    track_id: int = 0
    track: TrackModel = None

    @staticmethod
    def from_model(section: SectionModel) -> "Section":
        topics = (
            TopicModel.select()
            .join(SectionTopicsModel, on=(TopicModel.id == SectionTopicsModel.topic_id))
            .where(SectionTopicsModel.section_id == section.id)
            .order_by(SectionTopicsModel.order)
        )

        # this is mimicking the TrackItem.from_model function
        # circular imports are bad, so we can't import TrackItem here
        if section.track_id:
            track = TrackModel.get_by_id(section.track_id)
            track_dict = track.simple_dict()

        else:
            track_dict = TrackModel.empty_dict()

        return Section(
            id=section.id,
            start=section.start,
            end=section.end,
            video_id=section.video_id,
            section_type=section.section_type,
            track_id=section.track_id,
            track=track_dict,
            topics=[TopicItem.from_model(x) for x in topics],
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "start_string": str(timedelta(seconds=self.start / 1000)),
            "end_string": str(timedelta(seconds=self.end / 1000)),
            "video_id": self.video_id,
            "section_type": self.section_type,
            "track_id": self.track_id if self.track_id else 0,
            "track": self.track,
            "topics": [x.serialize() for x in self.topics],
        }

    @staticmethod
    def update_from_dict(item_id, new_data):
        section = SectionModel.get(SectionModel.id == item_id)
        section.start = new_data.get("start", section.start)
        section.end = new_data.get("end", section.end)
        section.section_type = new_data.get("section_type", section.section_type)
        section.save()

    @staticmethod
    def create_from_segment(segment: SuperchatSegmentItem):
        logger.debug(f"Creating Section from SuperchatSegment: {segment}")
        section = SectionModel.create(
            start=segment.start_time_milliseconds,
            end=segment.end_time_milliseconds,
            section_type="instrumental",
            video_id=segment.video_id,
        )
        segment.update_from_dict({"section_id": section.id})
        return section.id

    @staticmethod
    def delete_id(item_id):
        section = SectionModel.get_by_id(item_id)

        segment = (
            SuperchatSegmentModel.select()
            .where(SuperchatSegmentModel.section_id == item_id)
            .get_or_none()
        )
        if segment:
            segment.section_id = None
            segment.save()

        logger.debug(f"Deleting Section: {item_id}")
        SectionTopicsModel.delete().where(
            SectionTopicsModel.section_id == item_id
        ).execute()

        if section.track_id:
            track = TrackModel.get_by_id(section.track_id)
            for file in track.files:
                FileManager.delete_file(file.id)
            track.delete_instance(recursive=True)

        section.delete_instance()

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
    video_id: int = 0  # probably shouldn't be a default
    _sections: Section = field(init=False, default_factory=list)
    section_types: Optional[List[str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.section_types:
            self.section_types = self.ALLOWED_TYPES

        if self.duration <= 0:
            logger.error("Duration must be greater than 0")
            raise ValueError("Duration must be greater than 0")

    ##### definitely used functions (9/13/24)
    #### but probably shouldn't be 11/28/24...

    @property
    def sections(self):
        return self._sections

    @staticmethod
    def from_video(video) -> "SectionManager":
        sm = SectionManager(video_id=video.id, duration=video.duration)
        sm._sections = list(
            SectionModel.select(SectionModel.id, SectionModel.start, SectionModel.end)
            .where(SectionModel.video_id == video.id)
            .order_by(SectionModel.start)
        )
        return sm

    def save_to_db(self, section) -> None:
        new_sect = SectionModel.create(
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
        SectionModel.delete().where(SectionModel.id == section.id).execute()

    @staticmethod
    def get_by_id(id):
        logger.debug(
            "🧪🧪🧪🧪 get_by_id Is this is being used? get_by_id 9/13/24🧪🧪🧪🧪"
        )
        return SectionModel.get_or_none(SectionModel.id == id)

    @staticmethod
    def get_section_details(id):
        # this is in the SectionManager class, but its returning a Section object
        query = (
            SectionModel.select(
                SectionModel, TopicModel, SectionTopicsModel, TrackModel, FileModel
            )
            .join(
                SectionTopicsModel,
                on=(SectionModel.id == SectionTopicsModel.section_id),
                join_type=peewee.JOIN.LEFT_OUTER,
            )
            .join(
                TopicModel,
                join_type=peewee.JOIN.LEFT_OUTER,
            )
            .switch(SectionModel)
            .join(
                TrackModel,
                peewee.JOIN.LEFT_OUTER,
                on=(SectionModel.track_id == TrackModel.id),
            )
            .join(
                FileModel,
                peewee.JOIN.LEFT_OUTER,
                on=(TrackModel.id == FileModel.track_id),
            )
            .where(SectionModel.id == id)
        ).get_or_none()
        # logger.debug(f"Query Result: {query}")
        if query:
            return Section.from_model(query).serialize()
        else:
            return None

    @staticmethod
    def delete_section(id):
        SectionModel.delete().where(SectionModel.id == id).execute()
