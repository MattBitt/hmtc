import solara
import solara.lab
from solara.lab import task
from loguru import logger
import time
from hmtc.models import Video, VideoFile
from hmtc.config import init_config

updating = solara.reactive(False)


config = init_config()


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
    env = config.get("GENERAL", "ENVIRONMENT")

    @task
    def update():

        updating.set(True)
        result: solara.Result[bool] = solara.use_thread(some_task)
        if result.error:
            raise result.error
        updating.set(False)

    vids_in_db = Video.select().count()
    with solara.Column():
        solara.Markdown(f"## Environment = {env}")
        solara.Markdown(f"## Vids in DB: {vids_in_db}")
        solara.Markdown(f"DB Name {config.get('DATABASE', 'NAME')}")
    with solara.Card():

        if updating.value is True:
            solara.SpinnerSolara(size="100px")
        else:
            solara.Markdown("Not currently updating")
        with solara.Column():
            solara.Markdown("## Home")
            solara.Button("Update", on_click=update, disabled=updating.value)
