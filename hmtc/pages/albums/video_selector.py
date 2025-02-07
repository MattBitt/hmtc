import solara


@solara.component
def VideoSelector(album):
    solara.Text(f"Video Selector Component {album}")
    current_page = solara.use_reactive(1)
    total_pages = solara.use_reactive(album.videos_count())
    for dv in album.discs_and_videos():
        solara.Text(f"Videos Found {dv.title}")
