from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Track as TrackModel
from hmtc.models import TrackFiles
from hmtc.repos.file_repo import FileRepo
from hmtc.repos.track_repo import TrackRepo


class Track(BaseDomain):
    model = TrackModel
    repo = TrackRepo()
    file_repo = FileRepo(TrackFiles)

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "track_number": self.instance.track_number,
            "track_number_verbose": self.instance.track_number_verbose,
            "length": self.instance.length,
            "jellyfin_id": self.instance.jellyfin_id,
            "section_id": self.instance.section_id,
            "disc_id": self.instance.disc_id,
        }
