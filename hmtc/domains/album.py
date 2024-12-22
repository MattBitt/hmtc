from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Album as AlbumModel
from hmtc.repos.album_repo import AlbumRepo
from typing import Dict, Any


class Album(BaseDomain):
    model = AlbumModel
    repo = AlbumRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "release_date": str(self.instance.release_date),
        }
