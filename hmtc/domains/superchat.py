from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Superchat as SuperchatModel
from hmtc.repos.superchat_repo import SuperchatRepo


class Superchat(BaseDomain):
    model = SuperchatModel
    repo = SuperchatRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "frame": self.instance.frame,
            "video_id": self.instance.video_id,
            "segment_id": self.instance.segment_id,
        }
