from pathlib import Path

import PIL
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.vue_registry import register_vue_components
from hmtc.config import init_config
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
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import File as FileItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.section import SectionManager
from hmtc.schemas.series import Series as SeriesItem
from hmtc.schemas.track import Track as TrackItem
from hmtc.schemas.video import VideoItem
from hmtc.schemas.youtube_series import YoutubeSeries as YoutubeSeriesItem
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.utils.time_functions import seconds_to_hms, time_ago_string
from hmtc.utils.youtube_functions import download_video_file

IMG_WIDTH = "300px"


@solara.component
def VideoInfoPanelLeft(video):

    poster = FileManager.get_file_for_video(video, "poster")
    image = PIL.Image.open(Path(str(poster)))
    sections = SectionModel.select(
        SectionModel.id, SectionModel.start, SectionModel.end, SectionModel.track_id
    ).where(SectionModel.video_id == video.id)
    section_durations = [
        (x.end - x.start) / 1000 for x in sections
    ]  # list of sections in seconds
    section_percentage = sum(section_durations) / video.duration * 100
    tracks_created = len([x for x in sections if x.track_id is not None])

    def auto_create_tracks(*args):
        for section in sections:
            if section.track_id is None:
                album = AlbumModel.get_by_id(video.album_id)
                album_item = AlbumItem.from_model(album)
                track = album_item.create_from_section(section=section, video=video)
                section.track_id = track.id
                section.save()

    with solara.Row(justify="center"):
        solara.Text(
            f"{video.title[:80]}",
            classes=["video-info-text"],
        )
    with solara.Columns([6, 6]):
        with solara.Column():
            with solara.Row(justify="center"):
                solara.Image(image, width=IMG_WIDTH)
            with solara.Row(justify="center"):
                solara.Text(
                    f"Uploaded: {time_ago_string(video.upload_date)}",
                    classes=["medium-timer"],
                )
        with solara.Column():
            with solara.Row(justify="center"):
                if len(section_durations) > 0:
                    solara.Markdown(
                        f"Sections: {len(section_durations)} ({section_percentage:.2f}%)"
                    )
                    solara.Markdown(
                        f"Tracks Created: {tracks_created} ({tracks_created / len(section_durations) * 100:.2f}%)"
                    )
                else:
                    solara.Markdown("No Sections Found")
            with solara.Row(justify="center"):
                solara.Text(
                    f"Length: {seconds_to_hms(video.duration)}",
                    classes=["medium-timer"],
                )
            with solara.Row(justify="center"):
                solara.Button(
                    label=f"Create {len(sections)} Tracks",
                    classes=["button"],
                    disabled=(
                        (len(sections) <= tracks_created) or video.album_id is None
                    ),
                    on_click=auto_create_tracks,
                )