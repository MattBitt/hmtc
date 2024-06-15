from typing import List

import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video
from hmtc.mods.album import Album
from hmtc.mods.section import Section

title = "Video Album Editor"


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        raise ValueError("No video selected")

    return router.parts[level:][0]


def format_string(x: int):
    if x == 0:
        return "00:00:00"
    h, m, s = x // 3600, (x % 3600) // 60, x % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


### Don't know if this is true, but should be when finished
### reusable above this line
### below this line is the page definition


class State:
    loading = solara.reactive(False)
    album = solara.reactive(None)
    video = solara.reactive(None)

    @staticmethod
    def load_album():

        video_id = parse_url_args()
        vid = Video.get_by_id(video_id)
        album = Album.grab_for_video(video_id)
        if vid is not None:
            State.video.set(vid)
        if album is not None:
            State.album.set(album)

    @staticmethod
    def create_album():
        State.loading.set(True)

        album = Album.create_for_video(State.video.value)
        State.album.set(album)
        State.loading.set(False)

    @staticmethod
    def on_new(video, sections: List[Section]):

        # logger.debug(f"Adding new item: {start}, {end}, {section_type}")
        pass

    @staticmethod
    def on_delete(item):
        logger.debug(f"Deleting item: {item}")


@solara.component
def Page():

    State.load_album()

    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        with solara.Columns(6, 6):
            if State.loading.value:
                with solara.Column():
                    solara.SpinnerSolara(size="100px")
            else:
                with solara.Column():
                    solara.Markdown(f"# {State.video.value.title}")
                    if State.album.value is None:
                        solara.Button("Create Album", on_click=State.create_album)
                    # solara.Markdown(f"Duration: {format_string(State.video.duration)}")
                    # solara.Markdown(f"Album: {State.album.title}")
                    # solara.Markdown(f"Tracks: {len(State.album.tracks)}")
