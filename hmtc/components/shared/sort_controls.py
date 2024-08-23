import solara


@solara.component()
def SortButton(label, col_name, sort_by, sort_order, on_click):
    if sort_by == col_name:
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
        state.sort_by.value = "created_at"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.apply_filters()

    def sort_by_title():
        state.sort_by.value = "title"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.apply_filters()

    def sort_by_upload_date():
        state.sort_by.value = "upload_date"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.apply_filters()

    def sort_by_updated_date():
        state.sort_by.value = "updated_at"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.apply_filters()

    def sort_by_duration():
        state.sort_by.value = "duration"
        if state.sort_order.value == "asc":
            state.sort_order.value = "desc"
        else:
            state.sort_order.value = "asc"

        state.apply_filters()

    with solara.Row():
        SortButton(
            label="title",
            col_name="title",
            sort_by=state.sort_by.value,
            sort_order=state.sort_order.value,
            on_click=state.apply_filters,
        )
        SortButton(
            label="Created At",
            col_name="created_at",
            sort_by=state.sort_by.value,
            sort_order=state.sort_order.value,
            on_click=state.apply_filters,
        )

        SortButton(
            label="Upload Date",
            col_name="upload_date",
            sort_by=state.sort_by.value,
            sort_order=state.sort_order.value,
            on_click=state.apply_filters,
        )

        SortButton(
            label="Updated At",
            col_name="updated_at",
            sort_by=state.sort_by.value,
            sort_order=state.sort_order.value,
            on_click=state.apply_filters,
        )

        SortButton(
            label="Duration",
            col_name="duration",
            sort_by=state.sort_by.value,
            sort_order=state.sort_order.value,
            on_click=state.apply_filters,
        )
