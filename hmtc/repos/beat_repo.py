from hmtc.models import Beat as BeatModel
from hmtc.repos.base_repo import Repository


def BeatRepo():
    return Repository(
        model=BeatModel,
        label="Beat",
    )
