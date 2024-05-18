import solara


@solara.component
def StatsDisplay(playlists, total_playlist_count):

    items = playlists.value

    count_uniques = len([item for item in items if item.contains_unique_content])

    with solara.Row():
        solara.Text(f"Unique Content: ({count_uniques})")

    with solara.Row():
        solara.Text(f"Playlists: ({total_playlist_count})")
