import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import File as FileModel
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.schemas.superchat_segment import SuperchatSegment as SuperchatSegmentItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.image import are_images_similar
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper

config = init_config()


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        router.push("/videos")
    else:
        return router.parts[level:][0]


progress_total = solara.reactive(0)
progress_current = solara.reactive(0)
progress_title = solara.reactive("Searching for Superchats")
progress_subtitle = solara.reactive("Please wait...")
progress_message = solara.reactive("")


@solara.component
def Page():
    N_SECONDS = 10
    NUMBER_SUPERCHATS_DEV = 58  # 2 pages of 28 and a 3rd page of 2
    router = solara.use_router()
    MySidebar(router=router)

    searching = solara.use_reactive(False)

    video_id = parse_url_args()

    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))

    existing_superchats = (
        SuperchatModel.select()
        .where(SuperchatModel.video_id == video.id)
        .order_by(SuperchatModel.frame_number.asc())
    )

    superchats = [SuperchatItem.from_model(superchat=sc) for sc in existing_superchats]

    def search_for_superchats():
        searching.set(True)
        existing_frames = [sc.frame_number for sc in existing_superchats]
        progress_total.set(video.duration)
        progress_message.set(f"Searching for Superchats....")
        vf = [v for v in video.files if v.file_type == "video"][0]
        ie = ImageExtractor(Path(vf.path) / vf.filename)
        counter = 1
        before_loop = time.perf_counter()
        for frame in ie.frame_each_n_seconds(N_SECONDS):
            if (
                config["general"]["environment"] == "development"
                and counter > NUMBER_SUPERCHATS_DEV
            ):
                logger.warning(
                    f"Development mode, stopping after {NUMBER_SUPERCHATS_DEV} superchats"
                )
                break

            if ie.current_time in existing_frames:
                # for now, no reason to rerip superchats we already have
                continue

            sc_image, found = SuperChatRipper(frame).find_superchat()
            if found:
                sc = SuperchatModel.create(
                    frame_number=ie.current_time,
                    video_id=video.id,
                )
                sci = SuperchatItem.from_model(sc)
                sci.add_image(sc_image)
                counter += 1
            progress_current.set(progress_current.value + N_SECONDS)

            _message = f"Checking Frame: {progress_current.value}/{progress_total.value} ({progress_current.value/progress_total.value*100:.2f}%)\nElapsed Time: {time.perf_counter()-before_loop:.2f}s"
            progress_message.set(_message)

        ie.release_video()
        logger.success(f"Finished searching for superchats. Found {counter}")
        searching.set(False)
        progress_current.set(0)
        progress_total.set(0)

    def delete_all_superchats():
        searching.set(True)
        for sc in existing_superchats:
            sci = SuperchatItem.from_model(sc)
            sci.delete_me()
        searching.set(False)
        progress_current.set(0)
        progress_total.set(0)

    existing_segments = (
        SuperchatSegmentModel.select()
        .where(SuperchatSegmentModel.video_id == video.id)
        .order_by(SuperchatSegmentModel.start_time.asc())
    )

    def create_segments():
        searching.set(True)
        superchats = (
            SuperchatModel.select()
            .where(SuperchatModel.video_id == video.id)
            .order_by(SuperchatModel.frame_number.asc())
        )

        progress_total.set(len(superchats))
        progress_message.set(f"Searching for Superchat Segments....")

        before_loop = time.perf_counter()
        segment = None
        for _sc in superchats:

            if segment is None:
                segment = SuperchatSegmentItem.create_from_superchat(_sc)

            image1 = segment.get_image()

            superchat = SuperchatItem.from_model(_sc)
            image2 = superchat.get_image()

            if are_images_similar(image1, image2):
                segment.add_superchat(superchat)
            else:
                segment.close_segment(_sc.frame_number)
                new_segment = SuperchatSegmentItem.create_from_superchat(superchat)
                segment.set_next_segment(new_segment.id)
                segment = new_segment

            progress_current.set(progress_current.value + 1)
            _message = f"Analyzing Superchats: {progress_current.value}/{len(superchats)} ({progress_current.value/len(superchats)*100:.2f}%)\nElapsed Time: {time.perf_counter()-before_loop:.2f}s"
            progress_message.set(_message)

        searching.set(False)
        progress_current.set(0)
        progress_total.set(0)

    def delete_all_segments():
        searching.set(True)

        for segment in existing_segments:
            for sc in segment.superchats:
                sc.segment_id = None
                sc.save()
            segment_item = SuperchatSegmentItem.from_model(segment)
            segment_item.delete_me()
        searching.set(False)

    def create_all():
        search_for_superchats()
        create_segments()

    segments = [
        SuperchatSegmentItem.from_model(segment) for segment in existing_segments
    ]

    with solara.Column(classes=["main-container"]):
        with solara.Card():
            with solara.Columns([8, 4]):
                with solara.Column():
                    with solara.Row(justify="center"):
                        solara.Text(f"{video.title[:80]}")
                    with solara.Row(justify="space-around"):
                        solara.Text(
                            f"Superchats: {len(superchats)}", classes=["mysubtitle"]
                        )
                        solara.Text(
                            f"Segments: {len(segments)}", classes=["mysubtitle"]
                        )
                        solara.Text(
                            f"Duration: {(video.duration) / 60:.2f} minutes",
                            classes=["mysubtitle"],
                        )
        if searching.value:
            with solara.Card():
                with solara.Row(justify="center"):
                    if progress_total.value > 0:
                        with solara.Column():
                            solara.Text(
                                f"{progress_title.value}",
                                classes=["progress"],
                            )
                            solara.Text(
                                f"{progress_subtitle.value}", classes=["progress"]
                            )
                            solara.Text(
                                f"{progress_message.value}", classes=["progress"]
                            )

                            solara.ProgressLinear(
                                value=(progress_current.value / progress_total.value)
                                * 100,
                                classes=["progress-bar"],
                            )
                    else:
                        solara.Markdown("Searching for superchats...")
        else:

            if len(superchats) == 0:
                with solara.Card(title="No Superchats Found"):
                    solara.Text("No superchats found")
                    solara.Button(
                        label="Extract Superchats/Segments from Video",
                        icon_name="mdi-auto-fix",
                        on_click=create_all,
                        classes=["button"],
                        disabled=searching.value,
                    )
            else:
                with solara.Card(title="View Items"):
                    with solara.Row(justify="center"):
                        solara.Button(
                            label="Superchats",
                            icon_name="mdi-comment",
                            classes=["button"],
                            on_click=lambda: router.push(f"/superchats/{video.id}"),
                            disabled=(len(superchats) == 0) | searching.value,
                        )
                        solara.Button(
                            label="Superchat Segments",
                            icon_name="mdi-circle-slice-5",
                            classes=["button"],
                            on_click=lambda: router.push(
                                f"/superchat-segments/{video.id}"
                            ),
                            disabled=(len(segments) == 0) | searching.value,
                        )

                        solara.Button(
                            label="Superchat Segments (Long Enough)",
                            icon_name="mdi-circle-slice-5",
                            classes=["button"],
                            on_click=lambda: router.push(
                                f"/superchat-segments/long-enough/{video.id}"
                            ),
                            disabled=(len(segments) == 0) | searching.value,
                        )

                with solara.Card(title="Superchats Found"):
                    with solara.Row(justify="center"):
                        solara.Button(
                            label="Extract Superchats from Video",
                            icon_name="mdi-auto-fix",
                            on_click=search_for_superchats,
                            classes=["button"],
                            disabled=searching.value,
                        )

                        solara.Button(
                            label="Delete All Superchats",
                            icon_name="mdi-delete",
                            on_click=delete_all_superchats,
                            classes=["button", "mywarning"],
                            disabled=(len(superchats) == 0) | searching.value,
                        )

                with solara.Card(title="Superchat Segments"):
                    with solara.Row(justify="center"):
                        solara.Button(
                            label="Create Superchat Segments",
                            icon_name="mdi-auto-fix",
                            on_click=create_segments,
                            classes=["button"],
                            disabled=(len(superchats) == 0) | searching.value,
                        )

                        solara.Button(
                            label="Delete All Superchat Segments",
                            icon_name="mdi-delete",
                            on_click=delete_all_segments,
                            classes=["button", "mywarning"],
                            disabled=(len(segments) == 0) | searching.value,
                        )
