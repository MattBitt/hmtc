from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Beat as BeatModel
from hmtc.repos.beat_repo import BeatRepo
from typing import Dict, Any


class Beat(BaseDomain):
    model = BeatModel
    repo = BeatRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
        }
