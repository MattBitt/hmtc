import solara
import pandas as pd
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Video, Series


def get_videos():
    query = (
        Video.select()
        .join(Series)
        .order_by(Series)
        .order_by(Video.upload_date.desc())
        .limit(10)
    )
    return query


@solara.component
def VideosGroup():
    videos, set_videos = solara.use_state(None)
    loading, set_loading = solara.use_state(True)

    if loading:
        set_videos(get_videos())
        set_loading(False)

    else:
        with solara.ColumnsResponsive(12, large=[4, 4, 4]):
            for video in videos:
                with solara.Card():
                    solara.Markdown(video.title)


@solara.component
def Page():

    MyAppBar()
    with solara.lab.Tabs():
        with solara.lab.Tab("Tab 1"):
            VideosGroup()
        with solara.lab.Tab("Tab 2"):
            solara.Markdown("Pretend it's a different page")
            VideosGroup()
            solara.Markdown("World")
