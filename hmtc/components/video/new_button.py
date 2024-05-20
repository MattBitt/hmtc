from typing import Callable

import solara
from loguru import logger

from hmtc.schemas.video import VideoItem


@solara.component
def VideoNewButton(on_new: Callable[[VideoItem], None]):

    def create_new_item(*ignore_args):
        default_yt_id = "youtube_id"
        new_item = VideoItem.grab_by_youtube_id(youtube_id=default_yt_id)
        if new_item:
            logger.info(f"Item already exists: {new_item}")
            return
        new_item = VideoItem(
            title="Some Youtube Video", enabled=True, youtube_id="1234"
        )
        on_new(new_item)

    solara.Button("Create new Video Item (Default Text)", on_click=create_new_item)
