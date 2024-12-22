from pathlib import Path


from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


def VideoRepo():
    return Repository(
        model=VideoModel,
        label="Video",
    )
