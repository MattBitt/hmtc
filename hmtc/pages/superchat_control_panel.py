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
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper

config = init_config()


def are_images_similar(image1, image2):
    if (
        image1.shape[0] < 0.9 * image2.shape[0]
        or image1.shape[0] > 1.1 * image2.shape[0]
    ):
        return False
    if (
        image1.shape[1] < 0.9 * image2.shape[1]
        or image1.shape[1] > 1.1 * image2.shape[1]
    ):
        return False

    if image1.shape != image2.shape:
        if image1.shape[0] * image1.shape[1] > image2.shape[0] * image2.shape[1]:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
        else:
            image1 = cv2.resize(image1, (image2.shape[1], image2.shape[0]))

    def mse(imageA, imageB):
        # Compute the mean squared error between the two images
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        return err

    # Calculate the mean squared error and determine if images are similar
    mse_value = mse(image1, image2)
    threshold = 1500  # You can adjust this threshold value
    return mse_value < threshold


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
    NUMBER_SUPERCHATS_DEV = 18
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
        counter = 1
        for frame in ie.frame_each_n_seconds(N_FRAMES):
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

        ie.release_video()
        logger.success("Finished searching for superchats")
        searching.set(False)

    def create_segments():
        searching.set(True)
        segment = None
        for sc in existing_superchats:
            if segment is None:
                sc_item = SuperchatItem.from_model(sc)
                segment = SuperchatSegmentItem.create_from_superchat(sc_item)
                # initial segment gets the first superchat found
                continue

            image1 = segment.get_image()
            sc_item = SuperchatItem.from_model(sc)
            image2 = sc_item.get_image()
            if are_images_similar(image1, image2):
                segment.add_superchat(sc_item)
                continue
            else:
                # close out the current segment
                segment.close_segment(sc.frame_number)
                sc_item = SuperchatItem.from_model(sc)
                __segment = SuperchatSegmentItem.create_from_superchat(sc_item)
                segment.set_next_segment(__segment.id)
                segment = __segment
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
            for sc in segment.superchats:
                sc.segment_id = None
                sc.save()
            segment_item = SuperchatSegmentItem.from_model(segment)
            segment_item.delete_me()
        searching.set(False)

    superchats = [SuperchatItem.from_model(superchat=sc) for sc in existing_superchats]
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
                        classes=["button", "mywarning"],
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
                        classes=["button", "mywarning"],
                        disabled=len(segments) == 0,
                    )

        if searching.value:
            with solara.Card():
                solara.Markdown("Searching for Superchats")
