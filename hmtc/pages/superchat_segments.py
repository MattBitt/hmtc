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
def SuperchatSegmentCard(
    segment: SuperchatSegmentItem,
    combine_cards,
    delete_segment,
):
    img = segment.image.image
    _prev = segment.previous_segment.get_or_none()

    def merge_with_previous():
        # first segment in the function keeps the image
        if _prev is None:
            logger.error("No previous segment found")
            return
        prev = SuperchatSegmentItem.from_model(_prev)
        combine_cards(prev, segment)

    def merge_with_next():
        ns = segment.next_segment.get()
        nsi = SuperchatSegmentItem.from_model(ns)
        combine_cards(segment, nsi)

    if img is None:
        raise ValueError("No image found for segment")
    with solara.Card():
        with solara.Row(justify="space-between"):
            solara.Text(f"Segment ID: {segment.id}")
            solara.Text(f"Start: {segment.start_time}")
            solara.Text(f"End: {segment.end_time}")

            solara.Button(
                icon_name="mdi-delete",
                on_click=delete_segment,
                classes=["button", "warning"],
            )
        solara.Image(img, width="300px")
        with solara.Row(justify="space-between"):
            solara.Button(
                icon_name="mdi-arrow-left",
                classes=["button"],
                on_click=merge_with_previous,
                disabled=not bool(_prev),
            )
            solara.Text(f"<- Merge ->")
            solara.Button(
                icon_name="mdi-arrow-right",
                classes=["button"],
                on_click=merge_with_next,
                disabled=segment.next_segment is None,
            )
        with solara.Row(justify="center"):
            solara.Text(f"Duration: {segment.end_time - segment.start_time}")


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

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    existing_segments = (
        SuperchatSegmentModel.select()
        .where(SuperchatSegmentModel.video_id == video_id)
        .order_by(SuperchatSegmentModel.start_time.asc())
    )
    num_segments = existing_segments.count()
    num_pages = num_segments // NUM_IMAGES + 1
    existing_segments = existing_segments.paginate(current_page.value, NUM_IMAGES)

    segments = [SuperchatSegmentItem.from_model(seg) for seg in existing_segments]

    def combine_cards(segment1: SuperchatSegmentItem, segment2: SuperchatSegmentItem):
        SuperchatSegmentItem.combine_segments(segment1, segment2)
        refresh_trigger.set(refresh_trigger.value + 1)

    def delete_segment(segment_id):
        SuperchatSegmentItem.delete_id(segment_id)
        refresh_trigger.set(refresh_trigger.value + 1)

    if refresh_trigger.value > 0:
        with solara.Column(classes=["main-container"]):
            solara.Text(f"Superchat -> Sections Converter")
            PaginationControls(current_page, num_pages, num_segments)

            with solara.ColumnsResponsive(6):
                for segment in segments:
                    assert segment.image is not None
                    SuperchatSegmentCard(
                        segment,
                        combine_cards=combine_cards,
                        delete_segment=lambda: delete_segment(segment.id),
                    )