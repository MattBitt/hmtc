import solara


@solara.component
def StatsDisplay(stats):
    # with solara.Row():
    #     solara.Text(f"Unique Content: ({stats['unique']})")

    solara.Markdown(f"#### Total: **({stats['total']})**")
    solara.Markdown(f"#### Enabled: **({stats['enabled']})**")
    solara.Markdown(f"#### No Duration: **({stats['no_duration']})**")
