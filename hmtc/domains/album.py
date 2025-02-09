from typing import Any, Dict

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.base_domain import BaseDomain
from hmtc.domains.disc import Disc
from hmtc.models import Album as AlbumModel
from hmtc.models import AlbumFiles, db_null
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel
from hmtc.repos.album_repo import AlbumRepo
from hmtc.repos.file_repo import FileRepo

config = init_config()
db_instance = init_db(db_null, config)

# using this for swapping the order
# im sure there's a better way...
MAX_DISCS = 5000


class Album(BaseDomain):
    model = AlbumModel
    repo = AlbumRepo()
    file_repo = FileRepo(AlbumFiles)
    instance: AlbumModel = None

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
        logger.debug(f"Adding {video} to {self}")
        last_disc = (
            DiscModel.select(fn.MAX(DiscModel.order))
            .where(DiscModel.album_id == self.instance.id)
            .scalar()
        )
        if last_disc is None:
            last_disc = 1
        if existing_disc is not None:
            num_vids_on_existing_disc = DiscVideoModel.select().where(DiscVideoModel.disc_id == existing_disc.id).count()
            if num_vids_on_existing_disc == 0:
                order = 1
            else:
                order = num_vids_on_existing_disc
            new_dv = DiscVideoModel.create(
                video=video, disc=existing_disc, order=order
            )
            logger.success(f"Created disc video: {new_dv}")
        else:
            disc = DiscModel.create(
                title=f"Disc {last_disc+1}",
                order=last_disc + 1,
                album_id=self.instance.id,
            )
            logger.success(f"Created disc: {disc}")
            dv = DiscVideoModel.create(video=video, disc=disc, order=1)
            logger.success(f"Created disc video: {dv}")
        # how many discs do i have = n
        # create a disc 'Disc n+1'
        # create a discvideo

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
        disc_b = self.get_disc_before(order_a)
        if disc_b is None:
            logger.error(f"No Disc found before this one {disc.instance}")
            return
        disc_b = Disc(disc_b)
        order_b = disc_b.instance.order
        with db_instance.atomic():
            DiscModel.update(order=MAX_DISCS).where(
                DiscModel.id == disc.instance.id
            ).execute()
            DiscModel.update(order=order_a).where(
                DiscModel.id == disc_b.instance.id
            ).execute()
            DiscModel.update(order=order_b).where(
                DiscModel.id == disc.instance.id
            ).execute()

    def move_disc_down(self, disc):
        order_a = disc.instance.order
        disc_b = self.get_disc_after(order_a)
        if disc_b is None:
            logger.error(f"No Disc found after this one {disc.instance}")
            return
        disc_b = Disc(disc_b)
        order_b = disc_b.instance.order
        with db_instance.atomic():
            DiscModel.update(order=MAX_DISCS).where(
                DiscModel.id == disc.instance.id
            ).execute()
            DiscModel.update(order=order_a).where(
                DiscModel.id == disc_b.instance.id
            ).execute()
            DiscModel.update(order=order_b).where(
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
        logger.debug(f"{discs}")
        logger.debug(f"{ideal_disc_orders}")
        for x in zip(discs, ideal_disc_orders):
            if x[0].order != x[1]:
                logger.debug(f"Need to update {x[0]} to order: {x[1]}")
                x[0].order = x[1]
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
