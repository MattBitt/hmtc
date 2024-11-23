from dataclasses import dataclass
from pathlib import Path

import numpy as np
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
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
from hmtc.config import init_config

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
            if config["general"]["environment"] == "development" and counter > 5:
                logger.warning("Development mode, stopping after 5 frames")
                break

            if ie.current_time in existing_frames:
                # logger.debug(f"Skipping frame {ie.current_time}")
                continue
            # logger.error(f"Processing frame {ie.current_time}")
            sc_image, found = SuperChatRipper(frame).find_superchat()
            if found:
                # initially each superchat is its own segment
                # these will be combined later if the image matches
                new_segment = SuperchatSegmentModel.create(
                    start_time=ie.current_time,
                    end_time=ie.current_time,
                )

                sci = ImageManager(sc_image)

                sc = SuperchatItem(
                    image=sci.image,
                    frame_number=ie.current_time,
                    video=video,
                    superchat_segment=new_segment,
                )

                sc.save_to_db()
                sc.write_image(filename=f"{ie.current_time}.jpg")
                image_id = (
                    SuperchatFileModel.select()
                    .where(SuperchatFileModel.superchat_id == sc.id)
                    .get()
                    .id
                )
                new_segment.image_file_id = image_id
                new_segment.save()
                counter += 1

        ie.release_video()
        logger.success("Finished searching for superchats")
        searching.set(False)

    def delete_all_superchats():
        for sc in existing_superchats:
            sci = SuperchatItem.from_model(sc)
            sci.delete_me()

    superchats = [
        SuperchatItem(frame_number=sc.frame_number).from_model(superchat=sc)
        for sc in existing_superchats
    ]

    with solara.Column(classes=["main-container"]):
        with solara.Card():
            with solara.Columns([8, 4]):
                with solara.Column():
                    with solara.Row(justify="center"):
                        solara.Text(f"{video.title[:80]}")
                    with solara.Row(justify="space-between"):
                        solara.Text(f"Current Superchats: {len(superchats)}")
                        solara.Text(f"Total Frames: {video.duration}")
                with solara.Column():
                    solara.Button(
                        label="Superchat Segments",
                        classes=["button"],
                        on_click=lambda: router.push(f"/superchat-segments/{video.id}"),
                        disabled=len(superchats) == 0,
                    )
        with solara.Card():
            with solara.Row(justify="center"):
                solara.Button(
                    label="Search for Superchats",
                    on_click=search_for_superchats,
                    classes=["button"],
                )
                solara.Button(
                    label="Delete All Superchats",
                    on_click=delete_all_superchats,
                    classes=["button"],
                    disabled=len(superchats) == 0,
                )
        if searching.value:
            with solara.Card():
                solara.Markdown("Searching for Superchats")
