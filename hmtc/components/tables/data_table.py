from time import perf_counter

import solara
from loguru import logger


@solara.component
def DataTable(
    router,
    model,
    schema_item,
    base_query,
    headers,
    search_fields,
    vue_component,
    action1_path=None,
    action1_icon="",
    action2_path=None,
    action2_icon="",
    domain_class=None,
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
        if domain_class is None:
            logger.error(f"Saving {schema_item.item_type} Item: {args[0]['id']}")
            schema_item.update_from_dict(args[0]["id"], args[0])
        else:
            luc = args[0].get("last_update_completed")
            luc = str(luc) if luc is not None else None
            if luc is not None:
                if luc == "None":
                    args[0]["last_update_completed"] = None
            domain_class.update(args[0]["id"], args[0])

    def delete_item(*args):
        if domain_class is None:
            logger.error(f"Deleting {schema_item.item_type} Item: {args[0]['id']}")
            schema_item.delete_id(args[0]["id"])
        else:
            _item = domain_class().load(args[0]["id"])
            domain_class(_item).delete_me()

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

    # while converting to the 'domain' models, keep the tables working
    # with the 'from_model' algorithm
    if domain_class is None:
        items = [schema_item.from_model(item).serialize() for item in base_query]
    else:
        items = [domain_class(item).serialize() for item in base_query]

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
