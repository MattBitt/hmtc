import solara
import solara.lab
from solara.lab import task
from loguru import logger
import time
from hmtc.models import Video, VideoFile

updating = solara.reactive(False)


def disabled_videos_with_files():
    query = (
        Video.select()
        .join(VideoFile)
        .where(
            (Video.enabled == False)
            & (VideoFile.video_id.is_null(False))
            & (VideoFile.file_type.in_(["video", "audio"]))
        )
        .distinct()
    )
    return query.count()


def some_task():
    logger.debug("Update starts here")
    time.sleep(2)
    logger.debug("Update ends here")


@solara.component
def Page():
    counter = solara.use_reactive(0)

    @task
    def update():

        updating.set(True)
        result: solara.Result[bool] = solara.use_thread(some_task)
        if result.error:
            raise result.error
        updating.set(False)

    with solara.Column():
        solara.Markdown("## Stats")
        solara.Markdown(f"{disabled_videos_with_files()}")

    with solara.Card():

        if updating.value is True:
            solara.SpinnerSolara(size="100px")
        else:
            solara.Markdown("Not currently updating")
        with solara.Column():
            solara.Markdown("## Home")
            solara.Button("Update", on_click=update, disabled=updating.value)
