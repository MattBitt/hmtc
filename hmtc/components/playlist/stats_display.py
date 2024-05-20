import solara


@solara.component
def StatsDisplay(stats):

    with solara.Row():
        solara.Text(f"Unique Content: ({stats['unique']})")

    with solara.Row():
        solara.Text(f"Playlists: ({stats['total']})")

    with solara.Row():
        solara.Text(f"Enabled: ({stats['enabled']})")
