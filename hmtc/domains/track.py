from typing import List

from loguru import logger

from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.models import Disc as DiscModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.models import TrackFile as TrackFileModel
from hmtc.repos.base_repo import Repository
from hmtc.utils.file_manager import FileManager


class Track:
    repo = Repository(model=TrackModel(), label="Track")
    section_repo = Repository(model=SectionModel(), label="Section")
    disc_repo = Repository(model=DiscModel(), label="Disc")
    filetypes = ["poster", "thumbnail", "info"]
    file_manager = FileManager(model=TrackFileModel, filetypes=filetypes)

    @classmethod
    def create(cls, data) -> TrackModel:
        section = cls.section_repo.get_by(
            start=data["section"]["start"],
            end=data["section"]["end"],
            video_id=data["section"]["video_id"],
        )
        data["section"] = section

        disc = cls.disc_repo.get_by(id=data["disc"]["id"])
        data["disc"] = disc

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> TrackModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> TrackModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[TrackModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)

        _dict = item.my_dict()
        _dict["section"] = Section.serialize(item.section.id)

        _dict["disc"] = Disc.serialize(item.disc.id)
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
