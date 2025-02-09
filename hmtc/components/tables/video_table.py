import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.domains.video import Video
from hmtc.models import Video as VideoModel


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
    event_delete_item=None,
):
    pass


@solara.component
def VideoTable(router, headers, base_query, search_fields, sorted_dict={}):

    item_info = {
        "model": VideoModel,
        "vue_component": _VideoTable,
        "action1_path": "/api/videos/details",
        "action1_icon": "mdi-rhombus-split",
    }
    if sorted_dict != {}:
        item_info |= sorted_dict
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        domain_class=Video,
        **item_info,
    )
