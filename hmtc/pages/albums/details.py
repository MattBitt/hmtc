import solara

from hmtc.components.tables.video_table import VideoTable
from hmtc.models import (
    Video as VideoModel,
)


@solara.component
def Page():
    with solara.Column(classes=["main-container"]):
        solara.Text(f"Album Editor Page")
    router = solara.use_router()

    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Uploaded", "value": "upload_date", "sortable": True, "width": "10%"},
        {"text": "Title", "value": "title", "width": "30%"},
        {"text": "Duration", "value": "duration", "sortable": True},
    ]

    base_query = VideoModel.select().where(VideoModel.unique_content == True)
    search_fields = [VideoModel.youtube_id, VideoModel.title]
    VideoTable(
        router=router,
        headers=headers,
        base_query=base_query,
        search_fields=search_fields,
    )
