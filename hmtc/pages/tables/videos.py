from time import perf_counter
from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.video_table import VideoTable
from hmtc.domains.video import Video as VideoItem
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import (
    Channel,
    Series,
)
from hmtc.models import (
    Section as SectionModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.router import parse_url_args


def view_details(router, item):
    router.push(f"/domains/video-details/{item['id']}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)
    parse_url_args()

    base_query = VideoModel.select()
    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Title", "value": "title", "width": "30%"},
        {"text": "Duration", "value": "duration", "sortable": True},
        {"text": "Jellyfin ID", "value": "jellyfin_id", "sortable": False},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [VideoModel.youtube_id, VideoModel.title]
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
