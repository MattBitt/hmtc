from typing import List

from loguru import logger

from hmtc.domains.album import Album
from hmtc.models import Album as AlbumModel
from hmtc.models import Disc as DiscModel
from hmtc.models import Track as TrackModel
from hmtc.repos.base_repo import Repository


class Disc:
    repo = Repository(model=DiscModel(), label="Disc")
    album_repo = Repository(model=AlbumModel(), label="Album")

    @classmethod
    def create(cls, data) -> DiscModel:
        album = cls.album_repo.get(id=data["album_id"])
        data["album"] = album

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> DiscModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> DiscModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[DiscModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["album"] = Album.serialize(item.album.id)

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        from hmtc.domains.track import Track

        tracks = TrackModel.select().where(TrackModel.disc == item_id)

        for track in tracks:
            Track.delete_id(track.id)
        cls.repo.delete_by_id(item_id=item_id)