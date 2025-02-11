from typing import Any, Dict

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.base_domain import BaseDomain
from hmtc.domains.video import Video
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel
from hmtc.models import db_null
from hmtc.repos.disc_repo import DiscRepo
from hmtc.utils.general import paginate

config = init_config()
db_instance = init_db(db_null, config)


class Disc(BaseDomain):
    model = DiscModel
    repo = DiscRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "album_id": self.instance.album_id,
        }

    def num_videos_on_disc(self):
        return (
            DiscVideoModel.select(fn.COUNT(DiscVideoModel.id))
            .where(DiscVideoModel.disc_id == self.instance.id)
            .scalar()
        )

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
        orig_b = disc_vid_b.order
        tmp_order = 999

        disc_vid_a.order = tmp_order
        disc_vid_a.save()
        disc_vid_b.order = orig_a
        disc_vid_b.save()
        disc_vid_a.order = orig_b
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
