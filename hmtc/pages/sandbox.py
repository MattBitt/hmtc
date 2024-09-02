import solara
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionLine(
    timestamps=dict(
        whole_start=0,
        whole_end=2447,
        part_start=600,
        part_end=1200,
    )
):
    pass


def complicated_function(*args):
    logger.error(f"Running complicated Function with rgs = {args}")
    return args[0]


def set_section_type(*args):
    logger.error(f"Args = {args}")
    return args[0]


def load_next_section(*args):
    logger.debug("Loading Next Section:")
    # next_section(args[0])


def load_previous_section(*args):
    logger.debug("Loading Previous Section:")
    logger.error(f"Args = {args}")
    return args[0]


def func1(*args):
    logger.error(f"Calling Function 1 with args = {args}")
    return None


@solara.component
def Page():
    MySidebar(router=solara.use_router())

    solara.use_reactive(False)
    solara.use_reactive(True)
    new_topic = solara.use_reactive("")
    topics = solara.use_reactive(["football", "cats", "dogs"])
    video = dict(id=17, duration=1080)
    section = dict(id=15, start=182, end=687)
    dict(id=15, timestamp=section["start"], hour=1, minute=3, second=5)
    dict(id=37, timestamp=section["end"], hour=2, minute=3, second=4)
    dict(
        whole_start=0,
        whole_end=video["duration"],
        part_start=section["start"],
        part_end=section["end"],
    )

    def add_topic():
        if new_topic.value:
            topics.value.append(new_topic.value)
            new_topic.value = ""

    with solara.Column(classes=["main-container"]):
        solara.Markdown("## Sandbox")

        with solara.Card(
            elevation=10,
            margin="2",
        ):

            with solara.Card():
                SectionTimeButtons()
