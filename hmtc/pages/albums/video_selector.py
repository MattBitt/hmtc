import solara
from loguru import logger
from hmtc.domains.video import Video
from hmtc.models import (
    Video as VideoModel,
)
@solara.component_vue("./VideoSelector.vue", vuetify=True)
def _VideoTable(
    headers,
    items,
    current_page,
    total_items,
    total_pages,
    selected,
    event_item_selected,
    event_clear_search,
    event_new_options,
    event_search_for_item,
    event_change_page=None,
    event_next_page=None,
    event_previous_page=None,
    event_action1=None,
    event_save_item=None,
    event_delete_item=None,
):
    pass

def VideoTableMultiSelect(selected_videos, item_selected):
    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
         {"text": "Uploaded", "value": "upload_date", "sortable": True, "width": "10%"},
        {"text": "Title", "value": "title", "width": "30%"},
        {"text": "Duration", "value": "duration", "sortable": True},
    ]

    # base_query = VideoModel.select().where(VideoModel.unique_content == True)
    base_query = VideoModel.select()
    search_fields = [VideoModel.youtube_id, VideoModel.title]
    items = [Video(vid).serialize() for vid in base_query]
    for vid in selected_videos.value:
        solara.Text(f"{vid['title']}")
    
    _VideoTable(
        headers=headers,
        items=items,
        search_fields=search_fields,
        selected=selected_videos.value,
        current_page=1,
        total_items=5,
        total_pages=1,
        event_change_page=lambda x: logger.debug("change_page"),
        event_next_page=lambda x: logger.debug("next_page"),
        event_previous_page=lambda x: logger.debug("previous_page"),
        event_action1=lambda x: logger.debug("action1"),
        event_save_item=lambda x: logger.debug("save_item"),
        event_delete_item=lambda x: logger.debug("delete_item"),
        event_item_selected=item_selected,
        event_search_for_item=lambda x: logger.debug("searching for item"),
        event_clear_search=lambda x: logger.debug(f"clearing search"),
        event_new_options=lambda x: logger.debug(f"new_options"),
    )