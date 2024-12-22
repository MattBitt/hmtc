from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Section as SectionModel
from hmtc.repos.section_repo import SectionRepo


class Section(BaseDomain):
    model = SectionModel
    repo = SectionRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "start": self.instance.start,
            "end": self.instance.end,
            "section_type": self.instance.section_type,
            "video_id": self.instance.video_id,
        }
