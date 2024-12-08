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
from hmtc.domains.album import Album as AlbumItem
from hmtc.domains.section import Section as SectionItem
from hmtc.domains.series import Series as SeriesItem
from hmtc.domains.track import Track as TrackItem
from hmtc.domains.video import Video
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
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
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
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.time_functions import seconds_to_hms, time_ago_string
from hmtc.utils.youtube_functions import download_video_file

IMG_WIDTH = "300px"


@solara.component
def ProcessingCard():
    with solara.Card(
        classes=["processing-card"],
        style={"background-color": Colors.dark_gray},
    ):
        with solara.Row(justify="center"):
            MySpinner()
        with solara.Row(justify="center"):
            solara.Text("Processing...", classes=["processing-text"])


@solara.component
def VideoInfoPanel(video):

    # poster = FileManager.get_file_for_video(video, "poster")
    # image = ImageManager(poster).image
    background_processing = solara.use_reactive(0)
    sections = SectionModel.select(
        SectionModel.id, SectionModel.start, SectionModel.end
    ).where(SectionModel.video_id == video.id)

    def auto_create_tracks(*args):
        for section in sections:
            if section.track_id is None:
                album = AlbumModel.get_by_id(video.album_id)
                album_item = AlbumItem.from_model(album)
                track = album_item.create_from_section(section=section, video=video)
                section.save()

    section_durations = [
        (x.end - x.start) / 1000 for x in sections
    ]  # list of sections in seconds

    section_percentage = sum(section_durations) / video.duration * 100

    num_segments = (
        SuperchatSegmentModel.select()
        .where(SuperchatSegmentModel.video_id == video.id)
        .count()
    )

    with solara.Row(justify="center"):
        solara.Text(f"{background_processing.value}")
        solara.Text(
            f"{video.title[:80]}",
            classes=["video-info-text"],
        )
    with solara.Columns([6, 6]):
        with solara.Column():
            with solara.Row(justify="center"):
                solara.Markdown(f"Image Belongs Here")
                # solara.Image(image, width=IMG_WIDTH)
            with solara.Row(justify="center"):
                solara.Text(
                    f"Uploaded: {time_ago_string(video.upload_date)}",
                    classes=["medium-timer"],
                )
            with solara.Row(justify="center"):
                solara.Text(
                    f"Length: {seconds_to_hms(video.duration)}",
                    classes=["medium-timer"],
                )
        with solara.Column():
            with solara.Row(justify="center"):
                if len(section_durations) > 0:
                    solara.Markdown(
                        f"Sections: {len(section_durations)} ({section_percentage:.2f}%)"
                    )

            with solara.Row(justify="center"):
                with solara.Link(f"/frame-analyzer/{video.id}"):
                    solara.Button(
                        label="Frame Analyzer",
                        classes=["button"],
                    )
                with solara.Link(f"/superchat-fine-tuner/{video.id}"):
                    solara.Button(
                        label="Superchat Fine Tuner",
                        classes=["button"],
                    )

            with solara.Row(justify="center"):
                with solara.Link(f"/superchat-control-panel/{video.id}"):
                    solara.Button(
                        label="Search for Superchats",
                        icon_name="mdi-magnify",
                        classes=["button"],
                    )
            with solara.Row(justify="center"):
                if len(video.superchats) > 0:
                    with solara.Link(f"/superchat-segments/{video.id}"):
                        solara.Button(
                            label=f"Segments ({num_segments})",
                            icon_name="mdi-chat-processing",
                            classes=["button"],
                        )
            with solara.Row(justify="center"):
                if len(video.superchats) > 0:
                    with solara.Link(f"/superchat-segments/long-enough/{video.id}"):
                        solara.Button(
                            label=f"Segments (Long Enough)",
                            icon_name="mdi-chat-processing",
                            classes=["button"],
                        )
