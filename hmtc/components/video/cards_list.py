from typing import Callable

import solara
from solara.lab.toestand import Ref

from hmtc.components.video.list_item import VideoListItem


@solara.component
def VideoCards(
    videos,
    router,
    refreshing,
    on_save: Callable[[], None],
    on_update_from_youtube: Callable[[], None],
    on_delete: Callable[[], None],
):

    with solara.ColumnsResponsive(12, large=4):
        for index, item in enumerate(videos.value):
            refr = solara.use_reactive(False)
            # logger.debug(f"Rendering item {index} {item}")
            # logger.debug(f"Fields type = {type(videos.fields)} 🔵🔵🔵")
            if refr.value:
                solara.SpinnerSolara()
            else:

                VideoListItem(
                    Ref(videos.fields[index]),
                    router=router,
                    refreshing=refr,
                    on_save=on_save,
                    on_update_from_youtube=on_update_from_youtube,
                    on_delete=on_delete,
                )
