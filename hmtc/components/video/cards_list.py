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
            refr = solara.use_reactive(False)
            with solara.Card(style={"min-height": "250px"}):
                if refr.value:
                    solara.SpinnerSolara()
                else:
                    VideoListItem(
                        Ref(videos.fields[index]),
                        router=router,
                        refreshing=refr,
                        on_save=on_save,
                        on_delete=on_delete,
                        refresh_query=refresh_query,
                    )
