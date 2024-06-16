import solara


@solara.component()
def SortButton(label, col_name, sort_column, sort_order, on_click):
    if sort_column == col_name:
        if sort_order == "asc":
            icon_name = "mdi-arrow-up-bold"
        else:
            icon_name = "mdi-arrow-down-bold"
    else:
        icon_name = ""

    solara.Button(label=label, icon_name=icon_name, on_click=on_click)


@solara.component
def SortControls(state):
    def sort_by_created_date():
        state.sort_column.value = "created_at"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.refresh_query()

    def sort_by_title():
        state.sort_column.value = "title"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.refresh_query()

    def sort_by_upload_date():
        state.sort_column.value = "upload_date"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.refresh_query()

    def sort_by_updated_date():
        state.sort_column.value = "updated_at"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.refresh_query()

    with solara.Row():
        SortButton(
            label="Title",
            col_name="title",
            sort_column=state.sort_column.value,
            sort_order=state.sort_order.value,
            on_click=sort_by_title,
        )
        SortButton(
            label="Created At",
            col_name="created_at",
            sort_column=state.sort_column.value,
            sort_order=state.sort_order.value,
            on_click=sort_by_created_date,
        )

        SortButton(
            label="Upload Date",
            col_name="upload_date",
            sort_column=state.sort_column.value,
            sort_order=state.sort_order.value,
            on_click=sort_by_upload_date,
        )

        SortButton(
            label="Updated At",
            col_name="updated_at",
            sort_column=state.sort_column.value,
            sort_order=state.sort_order.value,
            on_click=sort_by_updated_date,
        )
