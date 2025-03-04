import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.sectionalizer import Sectionalizer
from hmtc.components.shared import Chip, PaginationControls
from hmtc.components.transitions.swap import SwapTransition
from hmtc.config import init_config
from hmtc.domains.section import Section
from hmtc.domains.superchat import Superchat
from hmtc.domains.topic import Topic
from hmtc.domains.video import Video

refresh = solara.reactive(1)
config = init_config()


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


time_cursor = solara.reactive(0)


@solara.component
def ControlPanel(video: Video, superchats: solara.Reactive, selected: solara.Reactive):
    LIMIT = 30

    # Create a reactive variable for superchats

    def find_sample():

        if config["general"]["environment"] == "development":
            limit = 1
        else:
            limit = None

        video.extract_superchats(limit)
        superchats.set(video.superchats())  # Update the reactive variable
        refresh.set(refresh.value + 1)

    def find_all():
        if config["general"]["environment"] == "development":
            limit = LIMIT
        else:
            limit = None
        video.extract_superchats(limit)
        superchats.set(video.superchats())  # Update the reactive variable
        refresh.set(refresh.value + 1)

    def delete_superchats():
        video.delete_superchats()
        superchats.set(video.superchats())  # Update the reactive variable
        refresh.set(refresh.value + 1)

    solara.Text(f"{video}")
    with solara.Columns([1, 2, 1]):

        with solara.Column():
            with SwapTransition(show_first=(len(superchats.value) == 0), name="fade"):
                with solara.Column():
                    solara.Button(
                        "Sample",
                        on_click=find_sample,
                        classes=["button"],
                        icon_name=Icons.SUPERCHAT.value,
                    )
                    solara.Button(
                        "All",
                        on_click=find_all,
                        classes=["button"],
                        icon_name=Icons.SUPERCHAT.value,
                    )
                with solara.Column():
                    solara.Button(
                        "Delete",
                        on_click=delete_superchats,
                        classes=["button mywarning"],
                        icon_name=Icons.SUPERCHAT.value,
                    )
        with solara.Column():
            solara.Image(video.poster(), width="400px")

        with solara.Column():
            for s in selected.value:
                solara.Markdown(f"### {s.instance.id}({s.instance.frame})")


@solara.component
def SuperchatCard(superchat, selected):

    def toggle(*args):

        if superchat in selected.value:
            logger.debug(
                f"toggling {superchat.instance.id}({superchat.instance.frame}) to NOT SELECTED"
            )
            selected.set(
                [x for x in selected.value if x.instance.id != superchat.instance.id]
            )
        else:
            logger.debug(
                f"toggling {superchat.instance.id}({superchat.instance.frame}) to SELECTED"
            )
            selected.set([*selected.value, superchat])

    style = {
        "width": "100%",
        "height": "100%",
        "display": "flex",
        "flex-direction": "column",
        "align-items": "stretch",
    }

    if superchat.instance.id in [s.instance.id for s in selected.value]:
        _class = ["seven-seg", "selected"]
    else:
        _class = ["version-number"]

    with solara.Button(on_click=toggle, style=style, classes=_class):
        Chip(str(superchat.instance.frame), color="info")
        solara.Image(superchat.poster(), width="300px")


@solara.component
def SuperchatList(superchats, selected):

    with solara.ColumnsResponsive(4, large=2):

        for _superchat in superchats.value:
            superchat = Superchat(_superchat)
            with solara.Row(justify="center", style={"height": "100px"}):
                SuperchatCard(superchat, selected)


@solara.component
def Page():

    video_id = parse_url_args()
    video = Video(video_id)
    current_page = solara.use_reactive(1)
    selected = solara.use_reactive([])
    per_page = 12

    _superchats, num_items, num_pages = video.superchats_paginated(
        current_page=current_page, per_page=per_page
    )

    superchats = solara.use_reactive(_superchats)

    if refresh.value > 0:
        with solara.Column(classes=["main-container"]):
            ControlPanel(video, superchats, selected)
            SuperchatList(superchats, selected)
            PaginationControls(
                current_page=current_page, num_pages=num_pages, num_items=num_items
            )
