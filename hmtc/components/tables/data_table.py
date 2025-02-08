from time import perf_counter

import solara
from loguru import logger


@solara.component
def DataTable(
    router,
    model,
    domain_class,
    base_query,
    headers,
    search_fields,
    vue_component,
    action1_path=None,
    action1_icon="",
    action2_path=None,
    action2_icon="",
):
    current_page = solara.use_reactive(1)
    current_sort_field = solara.use_reactive("id")
    current_sort_direction = solara.use_reactive("asc")
    per_page = solara.use_reactive(12)
    search_text = solara.use_reactive("")
    loading = solara.use_reactive(False)

    def clear_search(*args):
        loading.set(True)
        search_text.set("")
        logger.error("Clearing search")
        loading.set(False)

    def search_for_item(*args):
        loading.set(True)
        search_text.set(args[0])
        logger.error(f"Searching for item: {args[0]}")
        loading.set(False)

    def change_page(*args):
        loading.set(True)
        current_page.set(args[0])
        loading.set(False)

    def new_options(*args):
        loading.set(True)
        page = args[0]["page"]
        if page != current_page.value:
            current_page.set(page)
        if args[0]["sortBy"] != [] and (args[0]["sortBy"] != current_sort_field.value):
            current_sort_field.set(args[0]["sortBy"][0])
        if args[0]["sortDesc"] != []:
            if args[0]["sortDesc"][0] == True:
                current_sort_direction.set("desc")
            else:
                current_sort_direction.set("asc")
        loading.set(False)

    def save_item(*args):
        logger.debug(f"Saving {domain_class} Item: {args[0]['id']}")
        domain_class.get_by(id=args[0]["id"]).update(args[0])

    def delete_item(*args):
        # 12/22/24 this is untested (ish)
        logger.debug(f"Deleting {domain_class} Item: {args[0]['id']}")
        domain_class.get_by(id=args[0]["id"]).delete()

    if search_text.value != "":
        if len(search_fields) == 1:
            base_query = base_query.where(search_fields[0].contains(search_text.value))
        elif len(search_fields) > 1:
            # multiple fields to search through - combine them with OR
            expression = None
            for search_field in search_fields:
                if expression is None:
                    expression = search_field.contains(search_text.value)
                else:
                    expression = expression | search_field.contains(search_text.value)
            base_query = base_query.where(expression)

    sort_field = getattr(model, current_sort_field.value)
    if current_sort_direction.value == "asc":
        base_query = base_query.order_by(sort_field.asc())
    else:
        base_query = base_query.order_by(sort_field.desc())

    num_items = base_query.count()
    base_query = base_query.paginate(current_page.value, per_page.value)

    items = [domain_class(item.id).serialize() for item in base_query]

    vue_component(
        loading=loading.value,
        headers=headers,
        items=items,
        total_pages=(num_items // per_page.value) + 1,
        current_page=current_page.value,
        total_items=num_items,
        event_search_for_item=search_for_item,
        event_clear_search=lambda x: clear_search(x),
        event_new_options=new_options,
        event_change_page=lambda x: change_page(x),
        action1_icon=action1_icon,
        event_action1=lambda x: router.push(f"{action1_path}/{x['id']}"),
        action2_icon=action2_icon,
        event_action2=lambda x: router.push(f"{action2_path}/{x['id']}"),
        event_save_item=lambda x: save_item(x),
        event_delete_item=lambda x: delete_item(x),
    )
