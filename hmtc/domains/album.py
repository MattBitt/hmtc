import re
from pathlib import Path
from typing import Any, Dict

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.base_domain import BaseDomain
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.models import AlbumFiles, db_null
from hmtc.models import AlbumFiles as AlbumFilesModel
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Thumbnail as ThumbnailModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.repos.album_repo import AlbumRepo
from hmtc.repos.file_repo import FileRepo
from hmtc.utils.general import clean_filename, paginate

config = init_config()
db_instance = init_db(db_null, config)
STORAGE = Path(config["STORAGE"]) / "libraries"
# using this for swapping the order
# im sure there's a better way...
MAX_DISCS = 5000


class Album(BaseDomain):
    model = AlbumModel
    repo = AlbumRepo()
    file_repo = FileRepo(AlbumFiles)
    instance: AlbumModel = None
    libraries = ["audio", "video"]

    def folder(self, library):
        cleaned_title = clean_filename(self.instance.title)
        return STORAGE / f"{library}/Harry Mack/{cleaned_title}"

    def create_folders(self):
        cleaned_title = clean_filename(self.instance.title)
        for lib in self.libraries:
            folder = STORAGE / f"{lib}/Harry Mack/{cleaned_title}"
            folder.mkdir(exist_ok=True, parents=True)

    def add_file(self, file: Path, library: str):
        target_path = self.folder(library=library)

        # this is going to name everything as 'poster'
        # need to differentiate between filetypes at some
        # point.
        new_name = "poster"
        if not file.exists():
            raise ValueError(f"{file} doesn't exist. Quitting")
        self.file_repo.add(
            item=self.instance, source=file, target_path=target_path, stem=new_name
        )

    def serialize(self) -> Dict[str, Any]:
        num_discs = (
            DiscModel.select(fn.COUNT(DiscModel.id))
            .where(DiscModel.album_id == self.instance.id)
            .scalar()
        )
        my_discs = DiscModel.select(DiscModel.id).where(
            DiscModel.album_id == self.instance.id
        )
        num_videos = (
            DiscVideoModel.select(fn.COUNT(DiscVideoModel.video_id))
            .where(DiscVideoModel.disc_id.in_(my_discs))
            .scalar()
        )
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "release_date": self.instance.release_date.isoformat(),
            "num_discs": num_discs,
            "num_videos": num_videos,
        }

    def add_video(self, video: VideoModel, existing_disc=None):
        from hmtc.domains.video import Video

        logger.debug(f"Adding {video} to {self} ")
        last_disc = (
            DiscModel.select(fn.MAX(DiscModel.order))
            .where(DiscModel.album_id == self.instance.id)
            .scalar()
        )
        if last_disc is None:
            last_disc = 0
        if existing_disc is not None:
            num_vids_on_existing_disc = (
                DiscVideoModel.select()
                .where(DiscVideoModel.disc_id == existing_disc.id)
                .count()
            )
            if num_vids_on_existing_disc == 0:
                order = 1
            else:
                order = num_vids_on_existing_disc + 1
            new_dv = DiscVideoModel.create(video=video, disc=existing_disc, order=order)
            logger.success(f"Added video to existing: {existing_disc}")
        else:
            disc = DiscModel.create(
                title=f"Disc {str(last_disc+1).zfill(3)}",
                folder_name=f"Disc {str(last_disc+1).zfill(3)}",
                order=last_disc + 1,
                album_id=self.instance.id,
            )
            disc_item = Disc(disc.id)
            video_item = Video(video.id)
            disc_item.use_poster_from_video(video_item)
            logger.success(f"Created disc: {disc}")
            dv = DiscVideoModel.create(video=video, disc=disc, order=1)
            logger.success(f"Created disc video: {dv}")

    def videos_count(self):
        _discs = self.instance.discs
        vids = DiscVideoModel.select().where(DiscVideoModel.disc_id.in_(_discs)).count()
        return vids

    def discs_and_videos(self):
        base_query = (
            VideoModel.select()
            .join(DiscVideoModel, on=(VideoModel.id == DiscVideoModel.video_id))
            .join(DiscModel, on=(DiscModel.id == DiscVideoModel.disc_id))
            .where(DiscModel.album_id == self.instance.id)
        )
        return base_query

    def get_disc_before(self, order):
        return (
            DiscModel.select(DiscModel.id, DiscModel.order)
            .where((DiscModel.album_id == self.instance.id) & (DiscModel.order < order))
            .order_by(DiscModel.order.desc())
            .get_or_none()
        )

    def get_disc_after(self, order):
        return (
            DiscModel.select(DiscModel.id, DiscModel.order)
            .where((DiscModel.album_id == self.instance.id) & (DiscModel.order > order))
            .order_by(DiscModel.order.asc())
            .get_or_none()
        )

    def move_disc_up(self, disc: Disc):

        order_a = disc.instance.order
        folder_a = disc.instance.folder_name
        disc_b = self.get_disc_before(order_a)
        if disc_b is None:
            logger.error(f"No Disc found before this one {disc.instance}")
            return
        disc_b = Disc(disc_b)
        order_b = disc_b.instance.order
        folder_b = disc_b.instance.folder_name
        with db_instance.atomic():

            temp_folder_name = "Disc 999"
            DiscModel.update(order=MAX_DISCS, folder_name=temp_folder_name).where(
                DiscModel.id == disc.instance.id
            ).execute()
            DiscModel.update(order=order_a, folder_name=folder_a).where(
                DiscModel.id == disc_b.instance.id
            ).execute()
            DiscModel.update(order=order_b, folder_name=folder_b).where(
                DiscModel.id == disc.instance.id
            ).execute()

    def move_disc_down(self, disc):
        order_a = disc.instance.order
        folder_a = disc.instance.folder_name
        disc_b = self.get_disc_after(order_a)
        if disc_b is None:
            logger.error(f"No Disc found after this one {disc.instance}")
            return
        disc_b = Disc(disc_b)
        order_b = disc_b.instance.order
        folder_b = disc_b.instance.folder_name
        with db_instance.atomic():
            temp_folder_name = "Disc 999"
            DiscModel.update(order=MAX_DISCS, folder_name=temp_folder_name).where(
                DiscModel.id == disc.instance.id
            ).execute()
            DiscModel.update(order=order_a, folder_name=folder_a).where(
                DiscModel.id == disc_b.instance.id
            ).execute()
            DiscModel.update(order=order_b, folder_name=folder_b).where(
                DiscModel.id == disc.instance.id
            ).execute()

    def reset_disc_numbers(self):
        discs = (
            DiscModel.select(DiscModel.id, DiscModel.order)
            .where((DiscModel.album_id == self.instance.id) & (DiscModel.order != 0))
            .order_by(DiscModel.order.asc())
        )
        # actual_disc_orders = [x.order for x in discs]
        ideal_disc_orders = [x + 1 for x in range(len(discs))]
        logger.debug(f"{list(discs)}")
        logger.debug(f"{ideal_disc_orders}")
        for x in zip(discs, ideal_disc_orders):
            if x[0].order != x[1]:
                logger.debug(f"Need to update {x[0]} to order: {x[1]}")
                x[0].order = x[1]
                x[0].folder_name = f"Disc {x[1]}"
                x[0].title = f"Disc {x[1]}"
                x[0].save()

    def delete_discs(self):
        discs = (
            DiscModel.select(DiscModel.id, DiscModel.order)
            .where(DiscModel.album_id == self.instance.id)
            .order_by(DiscModel.order.asc())
        )
        for disc in discs:
            _disc = Disc(disc)
            _disc.delete()

    def discs_paginated(self, current_page, per_page):
        album_discs = (
            DiscModel.select()
            .where(DiscModel.album_id == self.instance.id)
            .order_by(DiscModel.order)
        )
        p = paginate(query=album_discs, page=current_page.value, per_page=per_page)

        return p

    def lock_discs(self):
        self.instance.discs_order_locked = True
        self.instance.save()

    def unlock_discs(self):
        self.instance.discs_order_locked = False
        self.instance.save()

    def tracks(self):
        discs = DiscModel.select().where(DiscModel.album_id == self.instance.id)
        return TrackModel.select().where(TrackModel.disc_id.in_(discs))

    def num_tracks(self):
        discs = DiscModel.select().where(DiscModel.album_id == self.instance.id)
        n = (
            TrackModel.select(fn.COUNT(TrackModel.id))
            .where(TrackModel.disc_id.in_(discs))
            .scalar()
        )
        if n is None:
            return 0
        else:
            return n

    def track_duration(self):
        discs = DiscModel.select().where(DiscModel.album_id == self.instance.id)
        n = (
            TrackModel.select(fn.SUM(TrackModel.length))
            .where(TrackModel.disc_id.in_(discs))
            .scalar()
        )
        if n is None:
            return 0
        else:
            return n

    def move_disc_to_compilation(self, disc: Disc):
        comp_disc = (
            DiscModel.select()
            .where(
                (DiscModel.title == "Disc 000")
                & (DiscModel.album_id == disc.instance.album.id)
            )
            .get_or_none()
        )
        if comp_disc is None:
            comp_disc = DiscModel.create(
                title=f"Disc 000",
                folder_name=f"Disc 000",
                order=0,
                album_id=disc.instance.album.id,
            )
        dv = disc.instance.dv.get_or_none()

        if dv is not None:
            video = Video(dv.video.id)

        _disc = Disc(comp_disc.id)

        self.add_video(video.instance, existing_disc=_disc.instance)
        disc.delete()
