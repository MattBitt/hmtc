from typing import List

from loguru import logger

from hmtc.domains.album import Album
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


class Track:
    repo = Repository(model=TrackModel(), label="Track")
    section_repo = Repository(model=SectionModel(), label="Section")

    @classmethod
    def create(cls, data) -> TrackModel:
        section = cls.section_repo.get(id=data["section_id"])
        data["section"] = section

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> TrackModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> TrackModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[TrackModel]:
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
