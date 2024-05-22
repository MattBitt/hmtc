import solara
from loguru import logger

from hmtc.config import init_config
from hmtc.schemas.video import VideoItem
from hmtc.states.base import State


class VideoSectionsState(State):
    logger.debug("Initializing Video Sections State object page = (Videos)")
    config = init_config()

    @classmethod
    def grab_video(cls, router, level):
        logger.debug(f"grab_video: {router.parts}")
        if len(router.parts) == 1:
            solara.Markdown("No Video Selected")
            return
        video_id = router.parts[level:][0]
        return VideoItem.grab_id_from_db(id=video_id)

    @classmethod
    def video_stats(cls):
        stats = {
            "total": VideoItem.count_enabled(),
            "enabled": VideoItem.count_enabled(),
            "disabled": VideoItem.count_enabled(enabled=False),
        }

        return stats
