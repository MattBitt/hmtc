from typing import Callable
from loguru import logger
import solara
from solara.lab.toestand import Ref

from hmtc.components.video.list_item import VideoListItem


@solara.component
def VideoCards(
    videos,
    router,
    on_save: Callable[[], None],
    on_update_from_youtube: Callable[[], None],
    on_delete: Callable[[], None],
):

    with solara.ColumnsResponsive(12, large=4):
        logger.error("Rendering Video Cards")
        logger.error(f"Videos count = {len(videos.value)}")
        for index, item in enumerate(videos.value):
            # logger.debug(f"Rendering item {index} {item}")
            # logger.debug(f"Fields type = {type(videos.fields)} 🔵🔵🔵")
            VideoListItem(
                Ref(videos.fields[index]),
                router=router,
                on_save=on_save,
                on_update_from_youtube=on_update_from_youtube,
                on_delete=on_delete,
            )
            # logger.debug("On to the next field 🏠🏠🏠")
