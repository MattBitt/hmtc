from datetime import date
from time import perf_counter
from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.video_table import VideoTable
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import (
    Channel as ChannelModel,
)
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import (
    Section as SectionModel,
)
from hmtc.models import (
    Series,
    VideoFiles,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.router import parse_url_args

refreshing = solara.reactive(0)
unique_options = ["unique", "nonunique", "all"]
unique = solara.reactive("unique")

missing_options = ["has", "missing", "all"]
has_video_file = solara.reactive("all")
has_album = solara.reactive("all")

channel_filter = solara.reactive("")


def view_details(router, item):
    router.push(f"/api/videos/{item['id']}")


@solara.component
def FilterBar():
    filter_string = ""
    channel_titles = [
        x.title
        for x in ChannelModel.select(ChannelModel.title).order_by(
            ChannelModel.title.asc()
        )
    ]

    def reset():
        unique.set("unique")
        has_video_file.set("all")
        has_album.set("all")
        channel_filter.set("")

    with solara.Card():
        with solara.Row():
            with solara.Columns():
                with solara.Column():
                    solara.Select(
                        label="Unique Videos", value=unique, values=unique_options
                    )
                with solara.Column():
                    solara.Select(
                        label="Has Video File",
                        value=has_video_file,
                        values=missing_options,
                    )
                with solara.Column():
                    solara.Select(
                        label="Has Album", value=has_album, values=missing_options
                    )
                with solara.Column():
                    solara.Select(
                        label="Channel",
                        value=channel_filter,
                        values=channel_titles,
                    )

        with solara.Row():
            solara.Button(f"Reset", on_click=reset, classes=["button"])


@solara.component
def NewVideo():
    new_item = solara.use_reactive("")
    error = solara.use_reactive("")
    success = solara.use_reactive("")

    def create_video():
        logger.debug(f"Creating new video {new_item.value} if possible")
        if len(new_item.value) <= 1:
            error.set(f"Value {new_item.value} too short.")
        else:
            try:
                new_video = Video.create_from_url(new_item.value)
                success.set(f"{new_video} was created!")
            except Exception as e:
                error.set(f"Error {e}")

    def reset():
        new_item.set("")
        error.set("")
        success.set("")

    with solara.Card():
        with solara.Columns([6, 6]):
            solara.InputText(label="Video Title", value=new_item)
            with solara.Row():
                solara.Button(
                    label="Create Video", on_click=create_video, classes=["button"]
                )
                solara.Button(label="Reset Form", on_click=reset, classes=["button"])
        if success.value:
            solara.Success(f"{success}")
        elif error.value:
            solara.Error(f"{error}")


@solara.component
def VideosPage():
    router = solara.use_router()

    args = parse_url_args()

    headers = [
        # {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Uploaded", "value": "upload_date", "sortable": True, "width": "10%"},
        {"text": "Title", "value": "title", "width": "30%"},
        {"text": "Sections", "value": "num_sections", "sortable": False},
        # {"text": "Album", "value": "album_title", "sortable": False},
        # {"text": "Channel", "value": "channel_title", "sortable": False},
        {"text": "Duration", "value": "duration", "sortable": True},
    ]

    if unique.value == "unique":
        base_query = VideoModel.select().where(VideoModel.unique_content == True)

    elif unique.value == "nonunique":
        base_query = VideoModel.select().where(VideoModel.unique_content == False)

    else:
        base_query = VideoModel.select()
        headers += [{"text": "Unique", "value": "unique_content", "sortable": False}]

    if has_video_file.value == "missing":
        vids_missing_files = [
            v.item_id
            for v in VideoFiles.select().where(VideoFiles.video_id.is_null(True))
        ]
        base_query = base_query.where(VideoModel.id.in_(vids_missing_files))

    if has_album.value == "missing":
        vids_with_albums = [
            dv.video_id for dv in DiscVideoModel.select(DiscVideoModel.video_id)
        ]
        base_query = base_query.where(VideoModel.id.not_in(vids_with_albums))
    elif has_album.value == "has":
        vids_with_albums = [
            dv.video_id for dv in DiscVideoModel.select(DiscVideoModel.video_id)
        ]
        base_query = base_query.where(VideoModel.id.in_(vids_with_albums))

    if channel_filter.value != "":
        channel = Channel.get_by(title=channel_filter.value)
        if channel is None:
            logger.error(f"Channel {channel_filter.value} not found...")
            return
        base_query = base_query.where(VideoModel.channel_id == channel.instance.id)

    headers += [
        # {"text": "Files", "value": "file_count", "sortable": False},
        {"text": "Actions", "value": "actions", "sortable": False, "align": "end"},
    ]

    search_fields = [VideoModel.youtube_id, VideoModel.title]
    NewVideo()
    FilterBar()
    VideoTable(
        router=router,
        headers=headers,
        base_query=base_query,
        search_fields=search_fields,
    )


# if filter == "wednesdays":
#     headers = [
#         {"text": "ID", "value": "id", "sortable": True, "align": "right"},
#         {"text": "Title", "value": "title", "width": "30%"},
#         {"text": "Episode", "value": "episode", "sortable": True},
#         {"text": "Superchats", "value": "superchats", "sortable": False},
#         {"text": "Segments", "value": "segments_count", "sortable": False},
#         {"text": "Actions", "value": "actions", "sortable": False},
#     ]
# else:
#     headers = [
#         {
#             "text": "Upload Date",
#             "value": "upload_date",
#             "sortable": True,
#             "width": "10%",
#         },
#         {"text": "ID", "value": "id", "sortable": True, "align": "right"},
#         {"text": "Title", "value": "title", "width": "30%"},
#         {"text": "Duration", "value": "duration", "sortable": True},
#         {
#             "text": "Sections",
#             "value": "section_info.section_count",
#             "sortable": False,
#         },
#         {"text": "Jellyfin ID", "value": "jellyfin_id", "sortable": False},
#         {"text": "Files", "value": "file_count", "sortable": False},
#         {"text": "Actions", "value": "actions", "sortable": False},
#     ]
