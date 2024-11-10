import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.models import Channel as ChannelModel
from hmtc.schemas.channel import Channel as ChannelItem


@solara.component_vue("ChannelTable.vue", vuetify=True)
def _ChannelTable(
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
def ChannelTable(router, headers, base_query, search_fields):
    item_info = {
        "model": ChannelModel,
        "schema_item": ChannelItem,
        "vue_component": _ChannelTable,
        "action1_path": "channels",
        "action1_icon": "mdi-cancel",
    }
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        **item_info,
    )
