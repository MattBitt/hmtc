from dataclasses import dataclass
from pathlib import Path

import numpy as np
import peewee
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.schemas.superchat_segment import SuperchatSegment as SuperchatSegmentItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper
from hmtc.components.shared.pagination_controls import PaginationControls


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        router.push("/videos")
    else:
        return router.parts[level:][0]


@solara.component
def SuperchatCard(
    superchat: SuperchatItem,
    refresh_trigger,
):
    img = superchat.image

    if img is None:
        raise ValueError("No image found for segment")

    def delete_superchat():
        logger.error(f"Deleting Superchat {superchat.id}")
        superchat.delete_me()
        refresh_trigger.set(refresh_trigger.value + 1)

    with solara.Card():
        with solara.Row(justify="space-between"):
            solara.Text(f"Frame Number: {superchat.frame_number}")
            solara.Button(
                icon_name="mdi-delete",
                on_click=delete_superchat,
                classes=["button", "warning"],
            )
        solara.Image(img, width="300px")


@solara.component
def Page():
    NUM_IMAGES = 6
    router = solara.use_router()
    MySidebar(router=router)
    current_page = solara.use_reactive(1)
    video_id = parse_url_args()
    refresh_trigger = solara.use_reactive(1)  # Add a reactive state for refresh
    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    existing_superchats = (
        SuperchatModel.select(SuperchatModel)
        .where(SuperchatModel.video_id == video_id)
        .order_by(SuperchatModel.frame_number.asc())
    )
    num_superchats = existing_superchats.count()
    num_pages = num_superchats // NUM_IMAGES
    existing_superchats = existing_superchats.paginate(current_page.value, NUM_IMAGES)

    if refresh_trigger.value > 0:
        with solara.Column(classes=["main-container"]):
            solara.Text(f"Superchats found for video {video_id}")
            PaginationControls(current_page, num_pages, num_superchats)

            with solara.ColumnsResponsive(6):
                for superchat in existing_superchats:
                    SuperchatCard(
                        SuperchatItem.from_model(superchat),
                        refresh_trigger=refresh_trigger,
                    )
