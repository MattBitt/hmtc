import solara


@solara.component
def SimpleProgressBar(label, value, color="blue"):
    with solara.Card():
        with solara.Row():
            solara.ProgressLinear(value=value, color=color)
        with solara.Row():
            solara.Markdown(f"{label} ({value:.0f}%)")
