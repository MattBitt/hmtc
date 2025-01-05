from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Album as AlbumModel
from hmtc.models import AlbumFiles
from hmtc.repos.album_repo import AlbumRepo
from hmtc.repos.file_repo import FileRepo


class Album(BaseDomain):
    model = AlbumModel
    repo = AlbumRepo()
    file_repo = FileRepo(AlbumFiles)
    instance: AlbumModel = None

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "release_date": self.instance.release_date.isoformat(),
        }
