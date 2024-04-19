import solara
import solara.lab
from solara.lab import task
from loguru import logger
import time

updating = solara.reactive(False)


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

    with solara.Card():

        if updating.value is True:
            solara.SpinnerSolara(size="100px")
        else:
            solara.Markdown("Not currently updating")
        with solara.Column():
            solara.Markdown("## Home")
            solara.Button("Update", on_click=update, disabled=updating.value)
