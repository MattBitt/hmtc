import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.models import File as FileModel
from hmtc.schemas.file import File as FileItem


@solara.component_vue("FileTable.vue", vuetify=True)
def _FileTable(
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
def FileTable(router, headers, base_query, search_fields):
    item_info = {
        "model": FileModel,
        "schema_item": FileItem,
        "vue_component": _FileTable,
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
