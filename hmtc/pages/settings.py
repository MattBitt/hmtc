import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Channel, Video as VideoTable
from hmtc.schemas.video import VideoItem
from loguru import logger
from hmtc.components.shared.progress_slider import SimpleProgressBar


class PageState:
    updating = solara.reactive(False)
    i = solara.reactive(0)
    num_to_download = solara.reactive(10)

    @staticmethod
    def download_empty_video_info():
        logger.debug("Downloading empty video info")
        PageState.updating.set(True)
        vids = (
            VideoTable.select()
            .where(VideoTable.duration.is_null())
            .limit(PageState.num_to_download.value)
        )
        logger.info(f"Updating {len(vids)} videos")
        for v in vids:
            vt = VideoItem.from_orm(v)
            try:
                vt.update_from_youtube()
            except Exception as e:
                logger.error(f"Error updating video: {e}")

            PageState.i.set(PageState.i.value + 1)
        logger.info("finished updating videos")
        PageState.i.set(0)
        PageState.updating.set(False)

    @staticmethod
    def refresh_videos_from_youtube():
        PageState.updating.set(True)
        channels = Channel.select().where(Channel.enabled == True)
        for c in channels:
            c.check_for_new_videos()
        PageState.updating.set(False)


@solara.component
def Page():
    router = solara.use_router()

    MySidebar(
        router=router,
    )

    with solara.Column(classes=["main-container"]):
        with solara.Column():
            if PageState.updating.value:
                with solara.Card():
                    solara.Text("Updating Videos")
                    SimpleProgressBar(
                        label="Videos Updated",
                        current_value=PageState.i.value,
                        total=PageState.num_to_download.value,
                        color="blue",
                    )
            else:
                with solara.Card():
                    solara.InputInt(
                        label="Number of Videos to Download",
                        value=PageState.num_to_download,
                    )
                    solara.Button(
                        label="Download info for 10 Random Videos!",
                        on_click=PageState.download_empty_video_info,
                        classes=["button"],
                    )
                with solara.Card():
                    solara.Button(
                        label="Check for New Videos",
                        on_click=PageState.refresh_videos_from_youtube,
                        classes=["button"],
                    )
