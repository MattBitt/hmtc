import solara


@solara.component
def SimpleProgressBar(label, current_value, total, color="blue"):
    if total == 0:
        with solara.Card():
            solara.Markdown(f"{label} (0 / 0) (0%)")
    else:
        with solara.Card():
            with solara.Row():
                solara.ProgressLinear(value=(current_value / total) * 100, color=color)
            with solara.Row():
                solara.Markdown(
                    f"{label} ({current_value} / {total}) ({(current_value / total)*100:.0f}%)"
                )
