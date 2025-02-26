from pathlib import Path
from typing import Any, Dict

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.base_domain import BaseDomain
from hmtc.domains.video import Video
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.models import db_null
from hmtc.repos.disc_repo import DiscRepo
from hmtc.utils.ffmpeg_utils import extract_audio, extract_video
from hmtc.utils.general import clean_filename, paginate
from hmtc.utils.mutagen_utils import write_id3_tags, write_mp4_metadata
from hmtc.utils.time_functions import seconds_to_hms

config = init_config()
STORAGE = Path(config["STORAGE"]) / "libraries"
db_instance = init_db(db_null, config)


class Disc(BaseDomain):
    model = DiscModel
    repo = DiscRepo()
    libraries = ["audio", "video"]

    def serialize(self) -> Dict[str, Any]:

        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "folder_name": self.instance.folder_name,
            "order": self.instance.order,
            "album_title": self.instance.album.title,
            "num_videos": self.num_videos_on_disc(),
        }

    def folder(self, library):
        cleaned_title = clean_filename(self.instance.album.title)
        return (
            STORAGE
            / f"{library}/Harry Mack/{cleaned_title}/{self.instance.folder_name}"
        )

    def create_folders(self):
        cleaned_title = clean_filename(self.instance.album.title)
        for lib in self.libraries:
            folder = (
                STORAGE
                / f"{lib}/Harry Mack/{cleaned_title}/{self.instance.folder_name}"
            )
            folder.mkdir(exist_ok=True, parents=True)

    def num_videos_on_disc(self):
        return (
            DiscVideoModel.select(fn.COUNT(DiscVideoModel.id))
            .where(DiscVideoModel.disc_id == self.instance.id)
            .scalar()
        )

    def disc_number(self):
        return int(self.instance.folder_name[-3:])

    def add_file(self, file: Path, library: str):
        year = self.instance.upload_date.strftime("%Y")
        target_path = self.folder(library=library)
        new_name = self.instance.youtube_id

        self.file_repo.add(
            item=self.instance, source=file, target_path=target_path, stem=new_name
        )

    def tracks(self):
        return TrackModel.select().where(TrackModel.disc_id == self.instance.id)

    def videos_paginated(self, current_page, per_page):
        disc_vids = (
            VideoModel.select()
            .join(DiscVideoModel, on=(VideoModel.id == DiscVideoModel.video_id))
            .where(
                VideoModel.id.in_(
                    DiscVideoModel.select(DiscVideoModel.video_id).where(
                        DiscVideoModel.disc_id == self.instance.id
                    )
                )
            )
            .order_by(DiscVideoModel.order.asc())
        )
        p = paginate(query=disc_vids, page=current_page.value, per_page=per_page)

        return p

    def swap_video_order(self, disc_vid_a: DiscVideoModel, disc_vid_b: DiscVideoModel):
        orig_a = disc_vid_a.order
        folder_a = disc_vid_a.disc.folder_name
        orig_b = disc_vid_b.order
        folder_b = disc_vid_b.disc.folder_name
        tmp_order = 999

        disc_vid_a.order = tmp_order
        disc_vid_a.save()
        disc_vid_b.order = orig_a
        disc_vid_b.save()
        disc_vid_b.disc.folder_name = folder_a
        disc_vid_b.disc.save()
        disc_vid_a.order = orig_b
        disc_vid_a.disc.folder_name = folder_b
        disc_vid_a.disc.save()
        disc_vid_a.save()

    def move_video_up(self, video: Video):
        disc_vid = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.video_id == video.instance.id)
            )
            .get()
        )
        target = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.order < disc_vid.order)
            )
            .order_by(DiscVideoModel.order.desc())
            .limit(1)
            .get_or_none()
        )
        if target is None:
            logger.error(f"Shouldn't be able to call this if theres no 'before' video")
            return

        logger.debug(f"swapping {disc_vid.order} and {target.order}")
        self.swap_video_order(disc_vid, target)

    def move_video_down(self, video: Video):
        disc_vid = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.video_id == video.instance.id)
            )
            .get()
        )
        target = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.order > disc_vid.order)
            )
            .order_by(DiscVideoModel.order.asc())
            .limit(1)
            .get_or_none()
        )
        if target is None:
            logger.error(f"Shouldn't be able to call this if theres no 'after' video")
            return

        logger.debug(f"swapping {disc_vid.order} and {target.order}")
        self.swap_video_order(disc_vid, target)

    def remove_video(self, video: Video):
        disc_vid = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.video_id == video.instance.id)
            )
            .get_or_none()
        )
        if disc_vid is None:
            logger.error(f"Disc Video not found.")
            return
        disc_vid.delete_instance()
        logger.success(f"Video {video} removed from Disc {self}")

    def num_tracks(self):
        num = (
            TrackModel.select(fn.COUNT(TrackModel.id))
            .where(TrackModel.disc_id == self.instance.id)
            .scalar()
        )
        if num is None:
            return 0
        return num

    def create_tracks(self):
        from hmtc.domains.section import Section
        from hmtc.domains.track import Track

        if self.num_videos_on_disc() > 1:
            logger.error(f"Not implemented yet")
            return
        if self.num_tracks() > 0:
            logger.error(f"Delete the tracks first")
            return
        dv = (
            DiscVideoModel.select()
            .where(DiscVideoModel.disc_id == self.instance.id)
            .get()
        )
        video = Video(dv.video.id)
        track_number = 0
        for section in video.sections():
            track_number += 1
            if track_number > 100:
                logger.error(f"Too many tracks!!!!!")
                return None

            logger.debug(f"Creating a track from {section}")
            sect = Section(section)
            prefix = self.instance.album.prefix
            disc_number = str(int(self.instance.folder_name[-3:]))
            if prefix is not None:
                if int(disc_number) >= 100:
                    title = f"{prefix}{disc_number}.{str(track_number).zfill(2)} {sect.my_title()}"
                else:
                    title = f"{prefix} {disc_number}.{str(track_number).zfill(2)} {sect.my_title()}"
            else:
                title = f"{sect.my_title()}"
            mp4_file_path = Path(self.folder("video")) / f"{title}.mp4"
            if mp4_file_path.exists():
                logger.error(f"{mp4_file_path} already exists. Quitting")
                return
            mp4_file_path.parent.mkdir(exist_ok=True, parents=True)

            mp3_file_path = Path(self.folder("audio")) / f"{title}.mp3"
            if mp3_file_path.exists():
                logger.error(f"{mp3_file_path} already exists. Quitting")
                return
            mp3_file_path.parent.mkdir(exist_ok=True, parents=True)

            input_file = Path(video.file_repo.get(video.instance.id, "video").path)
            if not input_file.exists():
                logger.error(f"{input_file} already exists. Quitting")
                return
            extract_video(
                input=input_file,
                output=mp4_file_path,
                start_time=seconds_to_hms(sect.instance.start // 1000),
                end_time=seconds_to_hms(sect.instance.end // 1000),
            )
            extract_audio(
                input=input_file,
                output=mp3_file_path,
                start_time=seconds_to_hms(sect.instance.start // 1000),
                end_time=seconds_to_hms(sect.instance.end // 1000),
            )

            new_track = Track.create_from_section(sect, track_number, self, title)
            write_id3_tags(mp3_file_path, new_track.id3_dict())
            new_track.file_repo.add(
                item=new_track.instance,
                source=mp4_file_path,
                target_path=mp4_file_path.parent,
                stem=mp4_file_path.name,
            )
            new_track.file_repo.add(
                item=new_track.instance,
                source=mp3_file_path,
                target_path=mp3_file_path.parent,
                stem=mp3_file_path.name,
            )

        logger.debug(f"Finished creating {track_number} tracks")

    def remove_tracks(self):
        from hmtc.domains.track import Track

        logger.debug(f"Disc {self} is about to remove its {self.num_tracks()} tracks.")
        for track in self.tracks():
            t = Track(track.id)
            t.delete()
