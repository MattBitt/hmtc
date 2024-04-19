import solara


@solara.component
def SingleSelect(title, selected, all):
    with solara.Div():
        solara.ToggleButtonsSingle(selected, all)
        # solara.Markdown(f"**Selected**: {selected.value}")
