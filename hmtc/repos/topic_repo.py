from hmtc.models import Topic as TopicModel
from hmtc.repos.base_repo import Repository


def TopicRepo():
    return Repository(
        model=TopicModel,
        label="Topic",
    )
