from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Disc as DiscModel
from hmtc.repos.disc_repo import DiscRepo
from typing import Dict, Any


class Disc(BaseDomain):
    model = DiscModel
    repo = DiscRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "album_id": self.instance.album_id,
        }
