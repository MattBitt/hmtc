from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Topic as TopicModel
from hmtc.repos.topic_repo import TopicRepo


class Topic(BaseDomain):
    model = TopicModel
    repo = TopicRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "text": self.instance.text,
        }
