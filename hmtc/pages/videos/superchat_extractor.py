import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.sectionalizer import Sectionalizer
from hmtc.components.shared import Chip, PaginationControls
from hmtc.domains.section import Section
from hmtc.domains.superchat import Superchat
from hmtc.domains.topic import Topic
from hmtc.domains.video import Video

refresh = solara.reactive(1)


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


time_cursor = solara.reactive(0)


@solara.component
def ControlPanel(video: Video):
    logger.debug(f"{video}")

    # Create a reactive variable for superchats
    superchats_list = solara.reactive([])

    def find_30():
        video.extract_superchats(30)
        superchats_list.set(video.superchats())  # Update the reactive variable
        refresh.set(refresh.value + 1)

    def find_all():
        video.extract_superchats()
        superchats_list.set(video.superchats())  # Update the reactive variable
        refresh.set(refresh.value + 1)

    def delete_superchats():
        video.delete_superchats()
        superchats_list.set(video.superchats())  # Update the reactive variable
        refresh.set(refresh.value + 1)

    solara.Text(f"{video}")
    with solara.Columns([1, 2, 1]):

        with solara.Column():
            solara.Button(
                "Find 30",
                on_click=find_30,
                classes=["button"],
                icon_name=Icons.SEARCH.value,
            )
            solara.Button(
                "Find All",
                on_click=find_all,
                classes=["button"],
                icon_name=Icons.SEARCH.value,
            )
            solara.Button(
                "Delete",
                on_click=delete_superchats,
                classes=["button mywarning"],
                icon_name=Icons.SUPERCHAT.value,
            )
        with solara.Column():
            solara.Image(video.poster(), width="400px")

        with solara.Column():
            solara.Button("click me")


@solara.component
def SuperchatList(superchats):

    with solara.ColumnsResponsive(4, large=2):

        for _superchat in superchats:
            superchat = Superchat(_superchat)
            with solara.Row(justify="center"):
                Chip(str(_superchat.frame), color="info")
                solara.Image(superchat.poster(), width="300px")


@solara.component
def Page():
    router = solara.use_router()
    video_id = parse_url_args()
    video = Video(video_id)
    current_page = solara.use_reactive(1)

    per_page = 12

    _superchats, num_items, num_pages = video.superchats_paginated(
        current_page=current_page, per_page=per_page
    )
    logger.debug(len(_superchats))
    if refresh.value > 0:
        with solara.Column(classes=["main-container"]):
            ControlPanel(video)
            SuperchatList(_superchats)
            PaginationControls(
                current_page=current_page, num_pages=num_pages, num_items=num_items
            )
