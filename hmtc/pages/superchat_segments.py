from dataclasses import dataclass
from pathlib import Path
import peewee
import numpy as np
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


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        router.push("/videos")
    else:
        return router.parts[level:][0]


@solara.component
def SuperchatSegmentCard(segment: SuperchatSegmentItem, before: int, after: int):
    img = segment.image.image

    def delete_segment():
        pass

    def merge_with_previous():
        # first segment in the function keeps the image
        main = SuperchatSegmentModel.get_by_id(segment.id)
        other = SuperchatSegmentModel.get_by_id(before)
        SuperchatSegmentItem.combine_segments(main, other)

    def merge_with_next():

        logger.debug(f"Merging {segment.id} with next segment {after}")

    if img is None:
        raise ValueError("No image found for segment")
    with solara.Card():
        with solara.Row(justify="space-between"):
            solara.Text(f"Start: {segment.start_time}")
            solara.Text(f"End: {segment.end_time})")
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
                disabled=before == 0,
            )
            solara.Button(
                icon_name="mdi-arrow-right",
                classes=["button"],
                on_click=merge_with_next,
                disabled=after == 0,
            )


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
        SuperchatModel.select(SuperchatModel, SuperchatSegmentModel, VideoModel)
        .join(
            VideoModel,
            peewee.JOIN.LEFT_OUTER,
            on=(SuperchatModel.video_id == VideoModel.id),
        )
        .switch(SuperchatModel)
        .join(
            SuperchatSegmentModel,
            peewee.JOIN.LEFT_OUTER,
            on=(SuperchatModel.superchat_segment_id == SuperchatSegmentModel.id),
        )
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

    segments = [
        SuperchatSegmentItem.from_model(sc.superchat_segment)
        for sc in superchats
        if sc.superchat_segment
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

        with solara.ColumnsResponsive(6):
            prev = 0
            if len(segments) <= 1:
                next = 0
            else:
                next = segments[1].id
            for segment in segments:
                SuperchatSegmentCard(segment, before=prev, after=next)
                prev = segment.id
                next = (
                    segments[segments.index(segment) + 2].id
                    if segments.index(segment) + 2 < len(segments)
                    else 0
                )
                logger.debug(f"Next: {next}")
