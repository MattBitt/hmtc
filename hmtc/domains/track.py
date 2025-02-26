from pathlib import Path
from typing import Any, Dict

from loguru import logger

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Thumbnail as ThumbnailModel
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

    def delete(self):
        # added this on 2/25/25.
        # copied from the videos domain

        tf = (
            TrackFiles.select()
            .where(TrackFiles.item_id == self.instance.id)
            .get_or_none()
        )
        if tf is not None:
            for ft in TrackFiles.FILETYPES:
                file_model = getattr(tf, ft)
                if file_model is not None:
                    if ft == "poster":
                        thumb = (
                            ThumbnailModel.select()
                            .where(ThumbnailModel.image_id == file_model.id)
                            .get()
                        )
                        Path(thumb.path).unlink()
                        thumb.delete_instance()
                    Path(file_model.path).unlink()
                    setattr(tf, ft, None)
                    tf.save()
                    file_model.delete_instance()
            tf.delete_instance()
        self.instance.delete_instance()

    @classmethod
    def create_from_section(cls, section, track_number, disc, title):
        length = (section.instance.end - section.instance.start) / 1000
        new_track = TrackModel.create(
            **{
                "title": title,
                "track_number": track_number,
                "length": length,
                "section_id": section.instance.id,
                "disc_id": disc.instance.id,
            }
        )
        return Track(new_track.id)

    def id3_dict(self):
        id3_tags = {}
        id3_tags["title"] = self.instance.title
        id3_tags["titlesort"] = self.instance.title

        id3_tags["artist"] = "Harry Mack"

        id3_tags["album"] = self.instance.disc.album.title
        id3_tags["albumsort"] = self.instance.disc.album.title
        id3_tags["albumartist"] = ["Harry Mack"]

        id3_tags["date"] = str(self.instance.section.video.upload_date)[0:4]
        id3_tags["originaldate"] = str(self.instance.section.video.upload_date)

        id3_tags["tracknumber"] = str(self.instance.track_number)
        id3_tags["discnumber"] = str(int(self.instance.disc.folder_name[-3:]))

        return id3_tags

    def create_nfo(self, folder):
        from hmtc.utils.xml_creator import create_track_xml

        nfo = folder / (f"{self.instance.title}.nfo")
        create_track_xml(nfo, self)
        return nfo
