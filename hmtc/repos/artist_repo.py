from hmtc.models import Artist as ArtistModel
from hmtc.repos.base_repo import Repository


def ArtistRepo():
    return Repository(
        model=ArtistModel,
        label="Artist",
    )
