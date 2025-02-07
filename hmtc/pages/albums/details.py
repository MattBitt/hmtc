import solara
from loguru import logger

from hmtc.domains.video import Video
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import (
    Disc as DiscModel,
)
from hmtc.models import (
    DiscVideo as DiscVideoModel,
)
from hmtc.models import (
    Video as VideoModel,
)

selected_videos = solara.reactive([])


def item_selected(item_dict):
    if item_dict["value"]:
        selected_videos.set([*selected_videos.value, item_dict["item"]])
    else:
        # remove this item from selected
        new_list = [
            vid for vid in selected_videos.value if vid["id"] != item_dict["item"]["id"]
        ]
        selected_videos.set(new_list)


@solara.component
def Page():
    with solara.Column(classes=["main-container"]):
        solara.Text(f"Album Editor Page")
    router = solara.use_router()
    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Title", "value": "title", "width": "30%"},
        {"text": "Order", "value": "order", "sortable": True},
    ]
    base_query = (
        VideoModel.select()
        .join(DiscVideoModel, on=(VideoModel.id == DiscVideoModel.video_id))
        .join(DiscModel, on=(DiscModel.id == DiscVideoModel.disc_id))
        .where(DiscModel.album_id == 1)
    )
    search_fields = [VideoModel.title]
    for item in base_query:
        solara.Text(f"{item}")
