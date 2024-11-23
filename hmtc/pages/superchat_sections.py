from dataclasses import dataclass
from pathlib import Path

import numpy as np
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        router.push("/videos")
    else:
        return router.parts[level:][0]


@solara.component
def SuperChatImageCard(superchat: SuperchatItem):
    img = superchat.get_image()
    if img is None:
        raise ValueError("No image found for superchat")
    with solara.Card():
        with solara.Row(justify="space-between"):
            solara.Text(f"Frame: {superchat.frame_number} (ID: {superchat.id})")
            solara.Button(
                icon_name="mdi-delete",
                on_click=lambda: superchat.delete_me(),
                classes=["button", "warning"],
            )
        solara.Image(img, width="300px")
        with solara.Row(justify="space-between"):
            solara.Button(icon_name="mdi-arrow-left", classes=["button"])
            solara.Button(icon_name="mdi-arrow-right", classes=["button"])


@solara.component
def Page():
    NUM_IMAGES = 6
    router = solara.use_router()
    MySidebar(router=router)
    current_page = solara.use_reactive(1)
    video_id = parse_url_args()

    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    existing_superchats = (
        SuperchatModel.select()
        .where(SuperchatModel.video_id == video.id)
        .order_by(SuperchatModel.frame_number.asc())
    )
    num_superchats = existing_superchats.count()
    num_pages = num_superchats // NUM_IMAGES
    existing_superchats = existing_superchats.paginate(current_page.value, NUM_IMAGES)

    superchats = [
        SuperchatItem(frame_number=sc.frame_number).from_model(superchat=sc)
        for sc in existing_superchats
    ]
    with solara.Column(classes=["main-container"]):
        solara.Text(f"Superchat -> Sections Converter")
        with solara.Row(justify="space-between"):
            solara.Button(
                "First",
                on_click=lambda: current_page.set(0),
                disabled=current_page.value == 1,
                classes=["button"],
            )
            solara.Button(
                "Previous Page",
                on_click=lambda: current_page.set(current_page.value - 1),
                disabled=current_page.value == 1,
                classes=["button"],
            )
            solara.Text(f"Current Page: {current_page.value} of {num_pages}")
            solara.Text(f"Total Superchats: {num_superchats}")
            solara.Button(
                "Next Page",
                on_click=lambda: current_page.set(current_page.value + 1),
                classes=["button"],
                disabled=current_page.value == num_pages,
            )
            solara.Button(
                "Last",
                on_click=lambda: current_page.set(num_pages),
                classes=["button"],
                disabled=current_page.value == num_pages,
            )

        # working pretty well, but if i search for superchats in the video,
        # and then click 'next page' it will search for superchats again and again
        # until i kill it

        with solara.ColumnsResponsive(6):
            for sc in superchats:
                SuperChatImageCard(sc)
