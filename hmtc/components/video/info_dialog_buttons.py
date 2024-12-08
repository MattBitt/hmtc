from pathlib import Path

import solara
from loguru import logger

from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.video.files_panel import FilesPanel
from hmtc.components.video.jf_panel import JFPanel
from hmtc.components.video.section_dialog_button import SectionDialogButton
from hmtc.config import init_config
from hmtc.domains.album import Album as AlbumItem
from hmtc.domains.section import Section as SectionItem
from hmtc.domains.series import Series as SeriesItem
from hmtc.domains.track import Track as TrackItem
from hmtc.domains.video import Video as VideoItem
from hmtc.domains.youtube_series import YoutubeSeries as YoutubeSeriesItem
from hmtc.models import Album as AlbumModel
from hmtc.models import (
    File as FileModel,
)
from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopics as SectionTopicsModel,
)
from hmtc.models import (
    Series as SeriesModel,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import (
    Track as TrackModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.models import (
    YoutubeSeries as YoutubeSeriesModel,
)
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.youtube_functions import download_video_file


@solara.component_vue("VideoInfoInputCard.vue")
def VideoInfoInputCard(
    albums,
    serieses,
    youtube_serieses,
    selectedAlbum,
    selectedSeries,
    selectedYoutubeSeries,
    episode_number,
    event_create,
    event_update,
    event_remove,
):
    pass


@solara.component
def InfoDialogButtons(
    video,
):
    force_update_counter = solara.use_reactive(1)
    vid_db = VideoModel.get_by_id(video.id)

    def create(*args):
        logger.debug(f"Generic Create Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]
        except Exception as e:
            logger.error(e)
            return

        try:
            match _type:
                case "album":
                    item_id = AlbumModel.create(**item)
                    vid_db.album = item_id
                    vid_db.save()
                    album_item = AlbumItem.from_model(item_id)
                    album_item.use_video_poster()

                case "series":
                    item_id = SeriesModel.create(**item)
                    vid_db.series = item_id
                    vid_db.save()

                case "youtube_series":
                    item_id = YoutubeSeriesModel.create(**item)
                    vid_db.youtube_series = item_id
                    vid_db.save()

                case _:
                    logger.error(f"Type {_type} not found")
                    return
            force_update_counter.set(force_update_counter.value + 1)

        except Exception as e:
            logger.error(e)
            return

    def update(*args):
        logger.debug(f"Generic Update Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]

        except Exception as e:
            logger.error(e)
            raise

        try:
            match _type:
                case "album":
                    item_id = AlbumModel.get_by_id(item["id"])
                    vid_db.album = item_id
                    vid_db.save()
                    album_item = AlbumItem.from_model(item_id)
                    # i think leaving this here will change the album poster
                    # every time the album is updated
                    album_item.use_video_poster()

                case "series":
                    item_id = SeriesModel.get_by_id(item["id"])
                    vid_db.series = item_id
                    vid_db.save()

                case "youtube_series":
                    item_id = YoutubeSeriesModel.get_by_id(item["id"])
                    vid_db.youtube_series = item_id
                    vid_db.save()

                case _:
                    logger.error(f"Type {_type} not found")
                    return
            force_update_counter.set(force_update_counter.value + 1)

        except Exception as e:
            logger.error(e)
            raise

    def remove(*args):
        logger.debug(f"Generic Remove Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]
        except Exception as e:
            logger.error(e)
            return

        try:
            match _type:
                case "album":
                    vid_db.album = None
                    vid_db.save()
                    AlbumItem.delete_if_unused(item["id"])

                case "series":
                    vid_db.series = None
                    vid_db.save()
                    SeriesItem.delete_if_unused(item["id"])
                case "youtube_series":
                    vid_db.youtube_series = None
                    vid_db.save()
                    YoutubeSeriesItem.delete_if_unused(item["id"])
                case _:
                    logger.error(f"Type {_type} not found")
                    return
            force_update_counter.set(force_update_counter.value + 1)
        except Exception as e:
            logger.error(e)
            return

        vid_db.save()
        logger.debug(f"Successfully removed item from video {args}")

    album_dicts = [
        dict(id=a.id, title=a.title)
        for a in AlbumModel.select().order_by(AlbumModel.title)
    ]

    youtube_series_dicts = [
        dict(id=a.id, title=a.title)
        for a in YoutubeSeriesModel.select().order_by(YoutubeSeriesModel.title)
    ]
    series_dicts = [
        dict(id=a.id, name=a.title)
        for a in SeriesModel.select().order_by(SeriesModel.title)
    ]

    try:
        this_album = [a for a in album_dicts if a["id"] == video.album_id][0]
    except IndexError:
        this_album = {"id": 0, "title": "None"}

    try:
        this_youtube_series = [
            x for x in youtube_series_dicts if x["id"] == video.youtube_series_id
        ][0]
    except IndexError:
        this_youtube_series = {"id": 0, "title": "None"}

    try:
        this_series = [x for x in series_dicts if x["id"] == video.series_id][0]
    except IndexError:
        this_series = {"id": 0, "name": "None"}

    if force_update_counter.value > 0:
        VideoInfoInputCard(
            albums=album_dicts,
            youtube_serieses=youtube_series_dicts,
            serieses=series_dicts,
            selectedAlbum=this_album,
            selectedYoutubeSeries=this_youtube_series,
            selectedSeries=this_series,
            episode_number=video.episode,
            event_create=create,
            event_update=update,
            event_remove=remove,
        )
