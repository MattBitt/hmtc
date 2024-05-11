import time

import solara
import solara.lab
from loguru import logger
from solara.lab import task

from hmtc.config import init_config
from hmtc.models import Video

# This is where the version is set for now.
# this ensures that whatever is running
# is the same as the rest of the code
# (instead of storing it in a separate file)

VERSION = "0.1.0"
config = init_config()
env = config["general"]["environment"]


updating = solara.reactive(False)


def disabled_videos_with_files():
    logger.error("This function is disabled")
    return
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

    vids_in_db = Video.select().count()
    with solara.Column():
        solara.Markdown(f"## Running Mode = {env}")
        solara.Markdown(f"## Version = {VERSION}")
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
