import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.domains.superchat import Superchat as SuperchatItem
from hmtc.models import Superchat as SuperchatModel


@solara.component_vue("SuperchatTable.vue", vuetify=True)
def _SuperchatTable(
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
def SuperchatTable(router, headers, base_query, search_fields):
    item_info = {
        "model": SuperchatModel,
        "vue_component": _SuperchatTable,
        "action1_path": "/superchat-details",
        "action1_icon": "mdi-user",
    }
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        domain_class=SuperchatItem,
        **item_info,
    )
