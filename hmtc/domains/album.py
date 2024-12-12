from typing import List

from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.models import Disc as DiscModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


class Album:
    repo = Repository(model=AlbumModel(), label="Album")
    disc_repo = Repository(model=DiscModel(), label="Disc")
    video_repo = Repository(model=VideoModel(), label="Video")

    @classmethod
    def create(cls, data) -> AlbumModel:
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> AlbumModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> AlbumModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[AlbumModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["release_date"] = str(_dict["release_date"])

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)

    @classmethod
    def add_video(cls, album_id, video_id, disc_id=None) -> None:
        album = cls.load(album_id)
        video = cls.video_repo.get(id=video_id)
        if disc_id is not None:
            disc = cls.disc_repo.get(id=disc_id)
        else:
            disc = DiscModel.create(title="Disc 1", album=album)
        video.disc = disc
        video.save()

    @classmethod
    def get_videos(cls, album_id) -> List[VideoModel]:
        album = cls.load(album_id)
        discs = DiscModel.select().where(DiscModel.album_id == album.id)
        return list(VideoModel.select().where(VideoModel.disc_id.in_(discs)))
