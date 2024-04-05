import solara
import pandas as pd
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Video


def get_videos():
    query = Video.select(Video.title, Video.duration, Video.upload_date).order_by(
        Video.upload_date.desc()
    )
    return pd.DataFrame(query.dicts())


@solara.component
def Page():

    MyAppBar()
    df = get_videos()

    with solara.Column(margin=4):

        solara.DataFrame(
            get_videos(),
            items_per_page=50,
        )
