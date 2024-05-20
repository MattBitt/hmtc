import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.video.list_item import VideoListItem


@solara.component
def VideoCards(videos, on_update, on_delete):

    with solara.ColumnsResponsive(12, large=4):
        for index, item in enumerate(videos.value):
            # logger.debug(f"Rendering item {index} {item}")
            logger.debug(f"Fields type = {type(videos.fields)} 🔵🔵🔵")
            VideoListItem(
                Ref(videos.fields[index]),
                on_update=on_update,
                on_delete=on_delete,
            )
            logger.debug("On to the next field 🏠🏠🏠")
