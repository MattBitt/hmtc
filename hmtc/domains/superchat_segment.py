from typing import List

from loguru import logger

from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


class SuperchatSegment:
    repo = Repository(model=SuperchatSegmentModel(), label="SuperchatSegment")
    section_repo = Repository(model=SectionModel(), label="Section")

    @classmethod
    def create(cls, data) -> SuperchatSegmentModel:
        if "_section" in data.keys():
            section = cls.section_repo.get_by(title=data["_section"]["title"])
            if section is None:
                raise ValueError(f"section {data['_section']} not found")
            del data["_section"]
        else:
            # not sure if this is the best way to handle this
            section = cls.section_repo.get_by(
                start=data["section"]["start"],
                end=data["section"]["end"],
                video_id=data["section"]["video_id"],
            )
        data["section"] = section

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> SuperchatSegmentModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> SuperchatSegmentModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[SuperchatSegmentModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()

        _dict["section"] = Section.serialize(item.section.id)

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
