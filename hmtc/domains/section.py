from typing import List

from loguru import logger

from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


class Section:
    repo = Repository(model=SectionModel(), label="Section")
    video_repo = Repository(model=VideoModel(), label="Video")

    @classmethod
    def create(cls, data) -> SectionModel:
        video = cls.video_repo.get(id=data["video_id"])
        data["video"] = video

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> SectionModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> SectionModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[SectionModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["video"] = Video.serialize(item.video.id)

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
