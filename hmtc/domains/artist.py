from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Artist as ArtistModel
from hmtc.repos.artist_repo import ArtistRepo


class Artist(BaseDomain):
    model = ArtistModel
    repo = ArtistRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "name": self.instance.name,
            "url": self.instance.url,
        }
