from pathlib import Path

import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        router.push("/domains/videos")
    else:
        return router.parts[level:][0]


@solara.component
def Page():

    router = solara.use_router()
    MySidebar(router=router)
    current_frame = solara.use_reactive(0)
    video_id = parse_url_args()
    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))

    # vid_file = FileManager.get_file_for_video(video, "video")
    vid_file = ""
    FRAME_INTERVAL = 0
    if vid_file.file_type == "":
        solara.Markdown(f"No video file found for video {video_id}")
        return
    else:
        file_path = Path(vid_file.path) / vid_file.filename

        image_extractor = ImageExtractor(file_path)
        FRAME_INTERVAL = image_extractor.fps
        num_frames = image_extractor.frame_count
        image = image_extractor.grab_frame(current_frame.value)

    def previous_frame(time_jump):
        if current_frame.value - FRAME_INTERVAL * time_jump < 0:
            current_frame.set(0)
        else:
            current_frame.set(current_frame.value - FRAME_INTERVAL * time_jump)

    def next_frame(time_jump):
        if current_frame.value + FRAME_INTERVAL * time_jump > num_frames:
            current_frame.set(num_frames)
        else:
            current_frame.set(current_frame.value + FRAME_INTERVAL * time_jump)

    def first_frame():
        current_frame.set(0)

    def last_frame():
        current_frame.set(num_frames)

    with solara.Column(classes=["main-container"]):
        with solara.Columns([6, 6]):
            with solara.Column():
                with solara.Row(justify="center"):
                    solara.Text(f"Current Time: {image_extractor.current_time}")
                with solara.Row(justify="center"):
                    solara.Text(f"Current Frame: {current_frame.value} / {num_frames}")
                with solara.Row(justify="center"):
                    solara.Text(f"Video Duration: {video.duration}")
                with solara.Row(justify="center"):
                    solara.Text(f"Frame Rate: {image_extractor.fps}")
            with solara.Row(justify="center"):
                solara.Image(image, width="600px")
        with solara.Row(justify="center"):
            solara.Button(
                "First Frame",
                first_frame,
                classes=["button"],
                disabled=current_frame.value == 0,
            )
            if video.duration > 600:
                solara.Button(
                    "-5 mins",
                    on_click=lambda: previous_frame(300),
                    classes=["button"],
                    disabled=current_frame.value == 0,
                )
            solara.Button(
                "-30 sec",
                on_click=lambda: previous_frame(30),
                classes=["button"],
                disabled=current_frame.value == 0,
            )
            solara.Button(
                "-1 sec",
                on_click=lambda: previous_frame(1),
                classes=["button"],
                disabled=current_frame.value == 0,
            )
            solara.Button(
                "+1 sec",
                on_click=lambda: next_frame(1),
                classes=["button"],
                disabled=current_frame.value == num_frames,
            )
            solara.Button(
                "+30 sec",
                on_click=lambda: next_frame(30),
                classes=["button"],
                disabled=current_frame.value == num_frames,
            )
            if video.duration > 600:
                solara.Button(
                    "+5 mins",
                    on_click=lambda: next_frame(300),
                    classes=["button"],
                    disabled=current_frame.value == num_frames,
                )
            solara.Button(
                "Last Frame",
                last_frame,
                classes=["button"],
                disabled=current_frame.value == num_frames,
            )
        superchat, found = SuperChatRipper(image).find_superchat()
        if found:
            solara.Image(superchat, width="80%")
