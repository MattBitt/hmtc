import solara


@solara.component
def SortControls(state):

    def sort_by_created_date():
        state.sort_column.value = "created_at"
        state.sort_order.value = "asc"
        state.refresh_query()

    def sort_by_title():
        state.sort_column.value = "title"
        state.sort_order.value = "asc"
        state.refresh_query()

    def sort_by_upload_date():
        state.sort_column.value = "upload_date"
        state.sort_order.value = "desc"
        state.refresh_query()

    def sort_by_updated_date():
        state.sort_column.value = "updated_at"
        state.sort_order.value = "desc"
        state.refresh_query()

    with solara.Row():
        solara.Button(label="Sort by Title", on_click=sort_by_title)
        solara.Button(label="Sort by Created Date", on_click=sort_by_created_date)
        solara.Button(label="Sort by Upload Date (desc)", on_click=sort_by_upload_date)
        solara.Button(
            label="Sort by Updated Date (desc)", on_click=sort_by_updated_date
        )
