import solara
from hmtc.assets.colors import Colors


@solara.component
def SimpleProgressBar(label, current_value, total, color="pink"):
    if total == 0:
        with solara.Card():
            solara.Markdown(f"{label} (0 / 0) (0%)")
    else:
        with solara.Card():
            _color = str(Colors.PRIMARY)
            with solara.Row():
                solara.ProgressLinear(
                    value=(current_value / total) * 100,
                    color=_color,
                    style={"height": "40px"},
                )
            with solara.Row():
                solara.Markdown(
                    f"{label} ({current_value} / {total}) ({(current_value / total)*100:.0f}%)"
                )
