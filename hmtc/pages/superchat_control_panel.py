from dataclasses import dataclass
from pathlib import Path

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


@solara.component
def Page():
    N_FRAMES = 10
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

    existing_segments = (
        SuperchatSegmentModel.select()
        .where(SuperchatSegmentModel.video_id == video.id)
        .order_by(SuperchatSegmentModel.start_time.asc())
    )

    def search_for_superchats():
        searching.set(True)

        existing_superchats = SuperchatModel.select(SuperchatModel.frame_number).where(
            SuperchatModel.video_id == video.id
        )
        existing_frames = [sc.frame_number for sc in existing_superchats]
        vf = [v for v in video.files if v.file_type == "video"][0]
        ie = ImageExtractor(Path(vf.path) / vf.filename)
        counter = 0
        for frame in ie.frame_each_n_seconds(N_FRAMES):
            if config["general"]["environment"] == "development" and counter > 18:
                logger.warning("Development mode, stopping after 15 superchats")
                break

            if ie.current_time in existing_frames:
                # logger.debug(f"Skipping frame {ie.current_time}")
                continue
            # logger.error(f"Processing frame {ie.current_time}")
            sc_image, found = SuperChatRipper(frame).find_superchat()
            if found:

                sci = ImageManager(sc_image)

                sc = SuperchatItem(
                    image=sci.image,
                    frame_number=ie.current_time,
                    video=video,
                )

                sc.save_to_db()
                sc.write_image(filename=f"{ie.current_time}.jpg")
                counter += 1

        ie.release_video()
        logger.success("Finished searching for superchats")
        searching.set(False)

    def create_segments():
        searching.set(True)
        new_segment = SuperchatSegmentModel.create(
            start_time=0, end_time=0, video_id=video.id
        )
        for sc in existing_superchats:
            if len(new_segment.files) == 0:
                # initial segment gets the first superchat found
                if len(sc.files) == 0:
                    logger.error(f"No files found for superchat {sc.id}. Skipping")
                    continue
                img = [i for i in sc.files if i.file_type == "image"][0]
                img.segment_id = new_segment.id
                img.save()
                continue
            if False:  # images are the same
                # start a new segment
                pass
            else:
                # close out the current segment
                new_segment.end_time = sc.frame_number
                new_segment.save()
                img = [i for i in sc.files if i.file_type == "image"][0]
                _new_segment = SuperchatSegmentModel.create(
                    start_time=sc.frame_number, end_time=0, video_id=video.id
                )
                new_segment.next_segment_id = _new_segment.id
                new_segment.save()
                new_segment = _new_segment
            logger.debug(f"Creating segment for {sc.frame_number}")
        searching.set(False)

    def delete_all_superchats():
        searching.set(True)
        for sc in existing_superchats:

            sci = SuperchatItem.from_model(sc)
            sci.delete_me()
        searching.set(False)

    def delete_all_segments():
        searching.set(True)
        for segment in existing_segments:
            segment_item = SuperchatSegmentItem.from_model(segment)
            segment_item.delete_me()
        searching.set(False)

    superchats = [
        SuperchatItem(frame_number=sc.frame_number).from_model(superchat=sc)
        for sc in existing_superchats
    ]
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
                        solara.Text(f"Superchats: {len(superchats)}")
                        solara.Text(f"Segments: {len(segments)}")
                        solara.Text(f"Duration: {video.duration}")
            with solara.Card(title="View Items"):
                with solara.Row(justify="center"):
                    solara.Button(
                        label="Superchats",
                        icon_name="mdi-comment",
                        classes=["button"],
                        on_click=lambda: router.push(f"/superchats/{video.id}"),
                        disabled=len(superchats) == 0,
                    )
                    solara.Button(
                        label="Superchat Segments",
                        icon_name="mdi-comment",
                        classes=["button"],
                        on_click=lambda: router.push(f"/superchat-segments/{video.id}"),
                        disabled=len(segments) == 0,
                    )

            with solara.Card(title="Superchats Found"):
                with solara.Row(justify="center"):
                    solara.Button(
                        label="Extract Superchats from Video",
                        icon_name="mdi-auto-fix",
                        on_click=search_for_superchats,
                        classes=["button"],
                    )

                    solara.Button(
                        label="Delete All Superchats",
                        icon_name="mdi-delete",
                        on_click=delete_all_superchats,
                        classes=["button", "warning"],
                        disabled=len(superchats) == 0,
                    )

            with solara.Card(title="Superchat Segments"):
                with solara.Row(justify="center"):
                    solara.Button(
                        label="Create Superchat Segments",
                        icon_name="mdi-comment",
                        on_click=create_segments,
                        classes=["button"],
                        disabled=len(superchats) == 0,
                    )

                    solara.Button(
                        label="Delete All Superchat Segments",
                        icon_name="mdi-delete",
                        on_click=delete_all_segments,
                        classes=["button", "warning"],
                        disabled=len(segments) == 0,
                    )

        if searching.value:
            with solara.Card():
                solara.Markdown("Searching for Superchats")
