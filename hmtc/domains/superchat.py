from typing import List

from loguru import logger

from hmtc.domains.video import Video
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


class Superchat:
    repo = Repository(model=SuperchatModel(), label="Superchat")
    video_repo = Repository(model=VideoModel(), label="Video")

    @classmethod
    def create(cls, data) -> SuperchatModel:
        if "_video" in data.keys():
            video = cls.video_repo.get_by(title=data["_video"]["title"])
            if video is None:
                raise ValueError(f"Video {data['_video']} not found")
            del data["_video"]
        else:
            # not sure if this is the best way to handle this
            video = cls.video_repo.get_by(title=data["video"]["title"])
        data["video"] = video

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> SuperchatModel:
        return cls.repo.get_by_id(item_id=item_id)

    @classmethod
    def update(cls, data) -> SuperchatModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[SuperchatModel]:
        return list(cls.repo.all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["video"] = Video.serialize(item.video.id)
        # if item.track is not None:
        #     _dict["track"] = Track.serialize(item.track.id)

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
