import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.models import Album as AlbumModel
from hmtc.schemas.album import Album as AlbumItem


@solara.component_vue("AlbumTable.vue", vuetify=True)
def _AlbumTable(
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
def AlbumTable(router, headers, base_query, search_fields):
    item_info = {
        "model": AlbumModel,
        "schema_item": AlbumItem,
        "vue_component": _AlbumTable,
        "action1_path": "/album-details",
        "action1_icon": "mdi-album",
    }
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        **item_info,
    )