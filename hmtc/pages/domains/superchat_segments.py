from dataclasses import dataclass
from pathlib import Path

import numpy as np
import peewee
import solara
from loguru import logger

from hmtc.components.shared.check_and_x.check_x import (
    Check,
    CheckClickable,
    X,
    XClickable,
)
from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.components.shared.sidebar import MySidebar

from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.utils.general import paginate
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        router.push("/domains/videos")
    match router.parts:
        case ["superchat-segments", "long-enough", video_id]:
            return (
                SuperchatSegmentModel.select()
                .where(
                    (SuperchatSegmentModel.video_id == video_id)
                    & (
                        (
                            SuperchatSegmentModel.end_time_ms
                            - SuperchatSegmentModel.start_time_ms
                        )
                        > 500
                    )
                )
                .order_by(SuperchatSegmentModel.start_time_ms.asc())
            ), True
        case ["superchat-segments", video_id]:
            return (
                SuperchatSegmentModel.select()
                .where(SuperchatSegmentModel.video_id == video_id)
                .order_by(SuperchatSegmentModel.start_time_ms.asc())
            ), False
        case _:
            logger.error(f"Invalid URL: {router.url}")
            router.push("/")


def merge_with_previous(segment, refresh_trigger):
    _prev = segment.previous_segment.get_or_none()
    prev = SuperchatSegmentItem.from_model(_prev)
    logger.error(f"About to add {len(segment.superchats)} superchats to {prev.id}")
    for sc in segment.superchats:
        prev.add_superchat(sc)
    _prev.end_time = segment.end_time
    _prev.save()

    if segment.next_segment is not None:
        next_segment = SuperchatSegmentItem.from_model(segment.next_segment)
        _prev.next_segment = next_segment.id
        _prev.save()
    segment.delete_me()

    refresh_trigger.set(refresh_trigger.value + 1)


def merge_with_next(segment, refresh_trigger):
    _prev = segment.previous_segment.get_or_none()
    next = SuperchatSegmentItem.from_model(segment.next_segment)
    logger.error(f"About to add {len(segment.superchats)} superchats to {next.id}")
    for sc in segment.superchats:
        next.add_superchat(sc)
    _next = SuperchatSegmentModel.get_by_id(next.id)
    _next.start_time = segment.start_time
    _next.save()

    if _prev is not None:
        _prev.next_segment = next.id
        _prev.save()
    segment.delete_me()
    refresh_trigger.set(refresh_trigger.value + 1)


def delete_segment(segment, refresh_trigger):
    segment.delete_me()
    refresh_trigger.set(refresh_trigger.value + 1)


@solara.component
def SuperchatSegmentCard(
    segment,
    long_enough,
    router,
    refresh_trigger,
):

    _prev = segment.previous_segment.get_or_none()

    with solara.Card():
        with solara.Row(justify="space-between"):
            if _prev is not None:
                solara.Text(f"prev: {_prev.id}")
            else:
                solara.Text("prev: None")
            solara.Text(f"ID: {segment.id}")

            if segment.next_segment is not None:
                solara.Text(f"next: {segment.next_segment.id}")
            else:
                solara.Text("next: None")
        with solara.Row(justify="space-between"):
            _start = int(segment.start_time * 60 / 1000)
            _end = int(segment.end_time * 60 / 1000)
            solara.Text(f"Superchats: {len(segment.superchats)}")
            solara.Text(
                f"{_start // 60:02}:{_start % 60:02}-{_end // 60:02}:{_end % 60:02}",
                classes=["seven-seg-tiny"],
            )
            solara.Text(
                f"{segment.duration* 60 / 1000:0.0f} s", classes=["seven-seg-tiny"]
            )
        image_ = segment.get_image()
        with solara.Row(justify="space-between"):
            if not long_enough:
                with solara.Columns([4, 8]):
                    solara.Button(
                        icon_name="mdi-delete",
                        on_click=lambda: delete_segment(segment, refresh_trigger),
                        classes=["button mywarning"],
                    )
                if image_ is not None:
                    solara.Image(segment.get_image(), width="200px")
            else:
                with solara.Column():
                    if image_ is not None:
                        solara.Image(segment.get_image(), width="400px")

        if not long_enough:
            with solara.Row(justify="center"):
                solara.Button(
                    icon_name="mdi-arrow-left",
                    classes=["button"],
                    on_click=lambda: merge_with_previous(segment, refresh_trigger),
                    disabled=not bool(_prev),
                )

                solara.Button(
                    icon_name="mdi-arrow-right",
                    classes=["button"],
                    on_click=lambda: merge_with_next(segment, refresh_trigger),
                    disabled=segment.next_segment is None,
                )
        else:
            solara.Button(
                icon_name="mdi-settings-helper",
                classes=["button"],
                on_click=lambda: router.push(f"/segment-editor/{segment.id}"),
            )
            if segment.section_id is not None:
                solara.Text(f"Section: {segment.section_id}")

                Check()
            else:
                solara.Button(
                    label="Create Section",
                    on_click=lambda: SectionItem.create_from_segment(segment),
                    classes=["button"],
                )


@solara.component
def SegmentsPanel(segments, long_enough, router, refresh_trigger):
    with solara.ColumnsResponsive(6):
        for segment in segments:
            SuperchatSegmentCard(
                segment,
                long_enough,
                router,
                refresh_trigger=refresh_trigger,
            )


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    current_page = solara.use_reactive(1)
    refresh_trigger = solara.use_reactive(1)  # Add a reactive state for refresh

    # long enough is a boolean that indicates if the segments are long enough
    # this view is more detailed and oriented towards creating sections from the
    # segments
    segment_query, long_enough = parse_url_args()
    if long_enough:
        per_page = 4
    else:
        per_page = 6

    query, num_items, num_pages = paginate(
        query=segment_query,
        page=current_page.value,
        per_page=per_page,
    )

    segments = [SuperchatSegmentItem.from_model(seg) for seg in query]

    if refresh_trigger.value > 0:
        with solara.Column(classes=["main-container"]):
            if num_pages > 0:
                PaginationControls(current_page, num_pages, num_items)
            SegmentsPanel(segments, long_enough, router, refresh_trigger)
