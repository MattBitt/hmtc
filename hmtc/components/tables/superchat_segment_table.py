import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.models import SuperchatSegment as SuperchatSegmentModel


@solara.component_vue("SuperchatSegmentTable.vue", vuetify=True)
def _SuperchatSegmentTable(
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
def SuperchatSegmentTable(router, headers, base_query, search_fields):
    item_info = {
        "model": SuperchatSegmentModel,
        "vue_component": _SuperchatSegmentTable,
        "action1_path": "/superchat_segment-details",
        "action1_icon": "mdi-cog",
    }
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        domain_class=SuperchatSegmentItem,
        **item_info,
    )
