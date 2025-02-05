import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.domains.track import Track
from hmtc.models import Track as TrackModel


@solara.component_vue("TrackTable.vue", vuetify=True)
def _TrackTable(
    loading,
    headers,
    items,
    current_page,
    total_pages,
    total_items,
    action1_icon="",
    action2_icon="",
    event_search_for_item=None,
    event_clear_search=None,
    event_new_options=None,
    event_change_page=None,
    event_next_page=None,
    event_previous_page=None,
    event_action1=None,
    event_action2=None,
    event_save_item=None,
    event_delete_item=None,
):
    pass


@solara.component
def TrackTable(router, headers, base_query, search_fields):
    item_info = {
        "model": TrackModel,
        "vue_component": _TrackTable,
        "action1_path": "/api/videos/details",
        "action1_icon": "mdi-rhombus-split",
        "action2_path": "/domains/album-details",
        "action2_icon": "mdi-album",
    }
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        domain_class=Track,
        **item_info,
    )
