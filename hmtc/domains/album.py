from typing import Any, Dict

from loguru import logger

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Album as AlbumModel
from hmtc.models import AlbumFiles
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel
from hmtc.repos.album_repo import AlbumRepo
from hmtc.repos.file_repo import FileRepo


class Album(BaseDomain):
    model = AlbumModel
    repo = AlbumRepo()
    file_repo = FileRepo(AlbumFiles)
    instance: AlbumModel = None

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "release_date": self.instance.release_date.isoformat(),
        }

    def add_video(self, video: VideoModel, existing_disc=None):
        logger.debug(f"Adding {video} to {self}")
        if existing_disc is not None:
            num_vids = len(existing_disc.videos)
            DiscVideoModel.create(video=video, disc=existing_disc, order=num_vids + 1)
        else:
            num_discs = DiscModel.select().where(DiscModel.album_id == self.instance.id).count()
            disc = DiscModel.create(title=f"Disc {num_discs+1}", order=1, album_id=self.instance.id)
            DiscVideoModel.create(video=video, disc=disc, order=1)
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
