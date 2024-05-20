import solara


@solara.component
def SortControls(state):

    def sort_by_date():
        state.sort_column.value = "created_at"
        state.sort_order.value = "asc"
        state.refresh_query()

    def sort_by_title():
        state.sort_column.value = "title"
        state.sort_order.value = "asc"
        state.refresh_query()

    with solara.Row():
        solara.Button(label="Sort by Title", on_click=sort_by_title)
        solara.Button(label="Sort by Date", on_click=sort_by_date)
