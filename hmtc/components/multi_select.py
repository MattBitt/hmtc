import solara


@solara.component
def MultiSelect(title, selected, all):
    with solara.Div():
        # solara.ToggleButtonsMultiple(selected, all, dense=True, style={"color": "blue"})

        def on_click(item):
            if item not in selected.value:
                selected.value.append(item)
            else:
                selected.value.remove(item)

        with solara.ToggleButtonsMultiple(
            value=selected, dense=False, style={"flex-wrap": "wrap"}
        ):
            # with solara.ColumnsResponsive(3):
            for item in all:
                solara.Button(
                    item,
                    value=item,
                    on_click=lambda: on_click(item),
                )
