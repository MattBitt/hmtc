from pathlib import Path
from typing import Any, Dict

from loguru import logger
from peewee import ModelSelect, fn
from PIL import Image

from hmtc.config import init_config
from hmtc.domains.base_domain import BaseDomain
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Section as SectionModel
from hmtc.models import Thumbnail as ThumbnailModel
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFiles
from hmtc.repos.file_repo import FileRepo
from hmtc.repos.video_repo import VideoRepo
from hmtc.utils.general import paginate
from hmtc.utils.youtube_functions import get_video_info

config = init_config()
STORAGE = Path(config["STORAGE"]) / "videos"
WORKING = Path(config["WORKING"])


class Video(BaseDomain):
    model = VideoModel
    repo = VideoRepo()
    file_repo = FileRepo(VideoFiles)

    def serialize(self) -> Dict[str, Any]:
        dv = (
            DiscVideoModel.select()
            .where(DiscVideoModel.video_id == self.instance.id)
            .get_or_none()
        )
        if dv is not None:
            album_title = dv.disc.album.title
        else:
            album_title = ""
        num_sections = (
            SectionModel.select(fn.COUNT(SectionModel.id))
            .where(SectionModel.video_id == self.instance.id)
            .scalar()
        )
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "description": self.instance.description,
            "duration": self.instance.duration,
            "upload_date": self.instance.upload_date.isoformat(),
            "url": self.instance.url,
            "youtube_id": self.instance.youtube_id,
            "unique_content": self.instance.unique_content,
            "jellyfin_id": self.instance.jellyfin_id,
            "channel_id": self.instance.channel_id,
            "file_count": self.file_repo.num_files(self.instance.id),
            "album_title": album_title,
            "channel_title": self.instance.channel.title,
            "num_sections": num_sections,
        }

    @classmethod
    def latest(cls, limit: int) -> ModelSelect:
        return (
            cls.repo.model.select()
            .where(cls.repo.model.unique_content == True)
            .order_by(cls.repo.model.upload_date.desc())
            .limit(limit)
        )

    def add_file(self, file: Path):
        year = self.instance.upload_date.strftime("%Y")
        target_path = STORAGE / year / self.instance.youtube_id
        new_name = self.instance.youtube_id

        self.file_repo.add(
            item=self.instance, source=file, target_path=target_path, stem=new_name
        )

    @classmethod
    def unique_count(cls):
        return (
            VideoModel.select(fn.COUNT(VideoModel.unique_content))
            .where(VideoModel.unique_content == True)
            .scalar()
        )

    # def delete(self):
    #     # added this on 2/15/25. didn't want to try to
    #     # dig into the 'chicago' file classes...
    #     logger.debug("deleting from the Video domain class")
    #     vf = (
    #         VideoFiles.select()
    #         .where(VideoFiles.item_id == self.instance.id)
    #         .get_or_none()
    #     )
    #     if vf is not None:
    #         for ft in VideoFiles.FILETYPES:
    #             file_model = getattr(vf, ft)
    #             if file_model is not None:
    #                 if ft == "poster":
    #                     thumb = (
    #                         ThumbnailModel.select()
    #                         .where(ThumbnailModel.image_id == file_model.id)
    #                         .get()
    #                     )
    #                     Path(thumb.path).unlink()
    #                     thumb.delete_instance()
    #                 Path(file_model.path).unlink()
    #                 setattr(vf, ft, None)
    #                 vf.save()
    #                 file_model.delete_instance()
    #         vf.delete_instance()
    #     self.instance.delete_instance()

    def delete_file(self, filetype) -> Path | None:
        _file = self.file_repo.delete(item_id=self.instance.id, filetype=filetype)
        logger.success(f"{_file} deleted")

    def sections_paginated(self, current_page, per_page):
        video_sections = self.sections()
        return paginate(
            query=video_sections, page=current_page.value, per_page=per_page
        )

    def sections(self):
        return (
            SectionModel.select()
            .where(SectionModel.video_id == self.instance.id)
            .order_by(SectionModel.start)
        )

    def album(self):
        from hmtc.domains.album import Album

        dv = (
            DiscVideoModel.select()
            .where(DiscVideoModel.video_id == self.instance.id)
            .get_or_none()
        )
        if dv is None:
            return None

        return Album(dv.disc.album)

    @classmethod
    def create_from_url(cls, url: str):
        from hmtc.utils.importer.existing_files import create_video_from_folder

        youtube_id = url[-11:]
        get_video_info(youtube_id, WORKING / youtube_id)
        create_video_from_folder(WORKING / youtube_id)
        new_vid = VideoModel.select().where(VideoModel.youtube_id == youtube_id).get()
        # if im creating it here,assume its unique
        new_vid.unique_content = True
        new_vid.save()
        return cls(new_vid.id)

    def create_single_section(self):
        from hmtc.domains.section import Section

        return Section.create(
            {
                "start": 0,
                "end": self.instance.duration * 1000,
                "section_type": "instrumental",
                "video_id": self.instance.id,
            }
        )

    def create_section(self, start, end, section_type="instrumental"):
        from hmtc.domains.section import Section

        if end > self.instance.duration:
            raise ValueError(
                f"{end} is greater than the duration {self.instance.duration}"
            )

        return Section.create(
            {
                "start": start * 1000,
                "end": end * 1000,
                "section_type": section_type,
                "video_id": self.instance.id,
            }
        )

    def __str__(self):
        if self.instance is None:
            return ""
        return str(self.instance.title)
