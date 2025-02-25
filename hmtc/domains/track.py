from pathlib import Path
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
    instance: TrackModel = None

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "track_number": self.instance.track_number,
            "track_number_verbose": self.instance.track_number_verbose,
            "length": self.instance.length,
            "jellyfin_id": self.instance.jellyfin_id,
            "section_id": self.instance.section.id,
            "disc_id": self.instance.disc.id,
        }

    def delete_file(self, filetype):
        _file = self.get_file(filetype)
        pass

    @classmethod
    def create_from_section(cls, section, track_number, disc):
        TrackModel.create(
            **{
                "title": "asdf",
                "track_number": track_number,
                "length": 15,
                "section_id": section.instance.id,
                "disc_id": disc.instance.id,
            }
        )
