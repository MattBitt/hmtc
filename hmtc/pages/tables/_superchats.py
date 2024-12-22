from dataclasses import dataclass
from pathlib import Path

import numpy as np
import peewee
import solara
from loguru import logger

from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.router import parse_url_args
from hmtc.utils.general import paginate
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper


@solara.component
def SuperchatCard(
    superchat,
    refresh_trigger,
):
    img = superchat.get_image()

    if img is None:
        raise ValueError("No image found for segment")

    def delete_superchat():
        logger.error(f"Deleting Superchat {superchat.id}")
        superchat.delete_me()
        refresh_trigger.set(refresh_trigger.value + 1)

    with solara.Card():
        with solara.Row(justify="space-between"):
            solara.Image(img, width="80px")
            solara.Button(
                icon_name="mdi-delete",
                on_click=delete_superchat,
                classes=["button", "mywarning"],
            )


@solara.component
def SuperchatsPanel(superchats, refresh_trigger):
    with solara.ColumnsResponsive(3):
        for superchat in superchats:
            SuperchatCard(
                superchat=superchat,
                refresh_trigger=refresh_trigger,
            )


@solara.component
def Page():

    router = solara.use_router()
    MySidebar(router=router)

    current_page = solara.use_reactive(1)
    refresh_trigger = solara.use_reactive(1)
    parse_url_args()

    segment_query = SuperchatSegmentModel.select(SuperchatSegmentModel).order_by(
        SuperchatSegmentModel.id.asc()
    )
    query, num_items, num_pages = paginate(
        query=segment_query,
        page=current_page.value,
        per_page=28,
    )

    superchats = [SuperchatItem.from_model(sc) for sc in query]

    if refresh_trigger.value > 0:
        with solara.Column(classes=["main-container"]):
            PaginationControls(current_page, num_pages, num_items)
            SuperchatsPanel(superchats, refresh_trigger)
