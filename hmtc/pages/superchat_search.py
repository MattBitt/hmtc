import solara
from pathlib import Path
from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.super_chat_ripper import SuperChatRipper
from hmtc.schemas.file import FileManager
from hmtc.schemas.video import VideoItem
from hmtc.models import Video as VideoModel


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        router.push("/videos")
    else:
        return router.parts[level:][0]


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    current_frame = solara.use_reactive(4200)

    video_id = parse_url_args()
    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    vid_file = FileManager.get_file_for_video(video, "video")

    if vid_file.file_type == "":
        solara.Markdown(f"No video file found for video {video_id}")
    else:
        file_path = Path(vid_file.path) / vid_file.filename

        image_extractor = ImageExtractor(file_path)
        images = image_extractor.extract_frame_sequence(80, 125, 10)
        for image in images:
            superchat, found = SuperChatRipper(image).find_superchat()
            with solara.Row():
                solara.Markdown(f"")
                solara.Image(image, width="68%")
                if found:
                    solara.Image(superchat, width="32%")
