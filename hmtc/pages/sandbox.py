import solara
from hmtc.models import Album as AlbumModel
from hmtc.schemas.album import Album as AlbumItem
from loguru import logger


@solara.component_vue("./sandbox.vue", vuetify=True)
def Sandbox(
    headers,
    items,
    current_page,
    total_pages,
    total_items,
    event_search_for_item=None,
    event_clear_search=None,
    event_new_options=None,
    event_change_page=None,
    event_next_page=None,
    event_previous_page=None,
):
    pass


headers = [
    {"text": "id", "value": "id"},
    {"text": "title", "value": "title"},
    {"text": "Release Date", "value": "release_date"},
]


@solara.component
def Page():
    solara.Markdown("Sandbox")
    current_page = solara.use_reactive(1)
    current_sort_field = solara.use_reactive("id")
    current_sort_direction = solara.use_reactive("asc")
    per_page = solara.use_reactive(12)
    search_text = solara.use_reactive("")
    loading = solara.use_reactive(False)

    def clear_search(*args):
        search_text.set("")
        logger.error("Clearing search")

    def search_for_item(*args):
        search_text.set(args[0])
        logger.error(f"Searching for item: {args[0]}")

    def change_page(*args):
        current_page.set(args[0])

    def previous_page(*args):
        current_page.set(current_page.value - 1)

    def next_page(*args):
        current_page.set(current_page.value + 1)

    def new_options(*args):
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

    sort_field = getattr(AlbumModel, current_sort_field.value)

    base_query = AlbumModel.select()
    if search_text.value != "":
        base_query = base_query.where(AlbumModel.title.contains(search_text.value))

    if current_sort_direction.value == "asc":
        base_query = base_query.order_by(sort_field.asc())
    else:
        base_query = base_query.order_by(sort_field.desc())

    num_albums = base_query.count()
    base_query = base_query.paginate(current_page.value, per_page.value)
    items = solara.use_reactive(
        [AlbumItem.from_model(item).serialize() for item in base_query]
    )
    with solara.Row():
        solara.Button(
            "Previous", on_click=previous_page, disabled=current_page.value == 1
        )
        solara.Button(
            "Next", on_click=next_page, disabled=current_page.value * 12 >= num_albums
        )
    Sandbox(
        headers=headers,
        items=items.value,
        total_pages=(num_albums // per_page.value) + 1,
        current_page=current_page.value,
        total_items=num_albums,
        event_search_for_item=search_for_item,
        event_clear_search=lambda x: clear_search(x),
        event_new_options=new_options,
        event_change_page=lambda x: change_page(x),
        event_next_page=lambda x: next_page(x),
        event_previous_page=lambda x: previous_page(x),
    )
