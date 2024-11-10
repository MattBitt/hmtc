import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.models import Series as SeriesModel
from hmtc.schemas.series import Series as SeriesItem


@solara.component_vue("SeriesTable.vue", vuetify=True)
def _SeriesTable(
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
def SeriesTable(router, headers, base_query, search_fields):
    item_info = {
        "model": SeriesModel,
        "schema_item": SeriesItem,
        "vue_component": _SeriesTable,
        "action1_path": "",
        "action1_icon": "",
    }
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        **item_info,
    )
