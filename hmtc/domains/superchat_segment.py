from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.repos.superchat_segment_repo import SuperchatSegmentRepo


class SuperchatSegment(BaseDomain):
    model = SuperchatSegmentModel
    repo = SuperchatSegmentRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "start_time_ms": self.instance.start_time_ms,
            "end_time_ms": self.instance.end_time_ms,
            "next_segment_id": self.instance.next_segment_id,
            "section_id": self.instance.section_id,
        }
