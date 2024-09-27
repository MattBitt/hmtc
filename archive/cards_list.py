from typing import Callable, List

import solara
from solara.lab.toestand import Ref

from hmtc.components.video.list_item import VideoListItem
from hmtc.schemas.video import VideoItem


@solara.component
def VideoCards(
    videos: solara.Reactive[List[VideoItem]],
    router,
    refreshing,
    refresh_query,
    on_save: Callable[[], None],
    on_delete: Callable[[], None],
):
    with solara.ColumnsResponsive(12, large=6):
        for index, item in enumerate(videos.value):
            with solara.Card(style={"min-height": "250px"}):
                if refreshing.value:
                    solara.SpinnerSolara()
                else:
                    if item is None:
                        solara.Alert("No videos found")
                    else:
                        VideoListItem(
                            Ref(videos.fields[index]),
                            router=router,
                            refreshing=refreshing,
                            on_save=on_save,
                            on_delete=on_delete,
                            refresh_query=refresh_query,
                        )
