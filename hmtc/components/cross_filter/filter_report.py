import solara
import solara.lab
from typing import List
import reacton.ipyvuetify as v


@solara.component
def FilterReport(df, classes: List[str] = []):
    # taken from solara.components.dataframe
    filter, set_filter = solara.use_cross_filter(id(df), "summary")
    dff = df
    filtered = False
    if filter is not None:
        filtered = True
        dff = df[filter]
    progress = len(dff) / len(df) * 100
    with solara.VBox(classes=classes) as main:
        solara.Markdown("## Filtered Count")
        with solara.HBox(align_items="center"):
            icon = "mdi-filter"
            v.Icon(children=[icon], style_="opacity: 0.1" if not filtered else "")
            if filtered:
                summary = f"{len(dff):,} / {len(df):,}"
            else:
                summary = f"{len(dff):,}"
            v.Html(tag="h3", children=[summary], style_="display: inline")
        # always add a progress bar to make sure the layout is the same
        if filtered:
            v.ProgressLinear(value=progress).key("visible")
        else:
            v.ProgressLinear(value=0, style_="visibility: hidden").key("hidden")

    return main
