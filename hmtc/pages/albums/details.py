import solara
from loguru import logger

from hmtc.domains.video import Video
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.pages.albums.video_selector import VideoTableMultiSelect
selected_videos = solara.reactive([])



def item_selected(item_dict):
    if item_dict['value']:
        selected_videos.set([*selected_videos.value, item_dict['item']])
    else:
        # remove this item from selected
        new_list = [vid for vid in selected_videos.value if vid['id'] != item_dict['item']['id']]
        selected_videos.set(new_list)

@solara.component
def Page():
    with solara.Column(classes=["main-container"]):
        solara.Text(f"Album Editor Page")
    router = solara.use_router()

    VideoTableMultiSelect(selected_videos,item_selected )
