import solara


@solara.component
def CenterSection(percent=80, children=None):
    offset = (100 - percent) / 2
    with solara.Columns([offset, percent, offset]):
        solara.Div()
        solara.Column(children=children)
        solara.Div()
