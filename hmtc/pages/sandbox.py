import solara
import ipyvue
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.section import SectionManager
from hmtc.schemas.video import VideoItem


@solara.component_vue("sandbox.vue")
def Sandbox():
    pass


topics = solara.reactive(["asdf", "qwer"])


@solara.component
def TopicInput():
    new_topic = solara.use_reactive("")

    def handle_submit():
        if new_topic.value and new_topic.value not in topics.value:
            topics.value.append(new_topic.value)
            new_topic.set("")

    def handle_cancel():
        new_topic.set("")

    with solara.VBox():
        solara.InputText(
            label="New Topic",
            value=new_topic,
        )
        with solara.HBox():
            solara.Button("Submit", on_click=handle_submit)
            solara.Button("Cancel", on_click=handle_cancel)


@solara.component
def TopicList():
    with solara.VBox():
        for topic in topics.value:
            solara.Text(topic)


@solara.component
def Page():
    Sandbox()
