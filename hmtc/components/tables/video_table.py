import solara
from loguru import logger
from hmtc.components.tables.data_table import DataTable
from hmtc.models import Video as VideoModel
from hmtc.schemas.video import VideoItem


@solara.component_vue("VideoTable.vue", vuetify=True)
def _VideoTable(
    loading,
    headers,
    items,
    current_page,
    total_pages,
    total_items,
    action1_icon="",
    event_search_for_item=None,
    event_clear_search=None,
    event_new_options=None,
    event_change_page=None,
    event_next_page=None,
    event_previous_page=None,
    event_action1=None,
    event_save_item=None,
):
    pass


@solara.component
def VideoTable(router, headers, base_query, search_fields):

    DataTable(
        router=router,
        model=VideoModel,
        schema_item=VideoItem,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        table_component=_VideoTable,
    )
