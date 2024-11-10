import solara
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel
from hmtc.components.tables.video_table import VideoTable


@solara.component
def Page():

    router = solara.use_router()
    MySidebar(router=router)
    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Title", "value": "title", "width": "20%"},
        {"text": "Youtube ID", "value": "youtube_id", "sortable": True},
        {"text": "Upload Date", "value": "upload_date", "sortable": True},
        {"text": "Actions", "value": "actions"},
    ]

    base_query = VideoModel.select().where(VideoModel.contains_unique_content == True)
    search_fields = [VideoModel.youtube_id, VideoModel.title]
    VideoTable(
        router=router,
        headers=headers,
        base_query=base_query,
        search_fields=search_fields,
    )
