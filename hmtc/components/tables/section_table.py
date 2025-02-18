import solara
from loguru import logger

from hmtc.components.tables.data_table import DataTable
from hmtc.domains.section import Section
from hmtc.models import Section as SectionModel


@solara.component_vue("SectionTable.vue", vuetify=True)
def _SectionTable(
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
def SectionTable(router, headers, base_query, search_fields):
    item_info = {
        "model": SectionModel,
        "vue_component": _SectionTable,
        "action1_path": "",
        "action1_icon": "",
    }
    DataTable(
        router=router,
        base_query=base_query,
        headers=headers,
        search_fields=search_fields,
        domain_class=Section,
        **item_info,
    )
