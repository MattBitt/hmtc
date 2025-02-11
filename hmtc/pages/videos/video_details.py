from pathlib import Path

import solara
import solara.lab
from flask import session
from loguru import logger

from hmtc.components.sectionalizer import Sectionalizer
from hmtc.components.video.video_info_panel import VideoInfoPanel
from hmtc.components.vue_registry import register_vue_components
from hmtc.config import init_config
from hmtc.domains.album import Album
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.utils.youtube_functions import download_video_file, get_video_info

config = init_config()
WORKING = config["WORKING"]


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


sections = solara.reactive([])
selected = solara.reactive({})


@solara.component_vue("./SectionSelector.vue", vuetify=True)
def SectionSelector(
    sections, selected, video_duration, event_remove_section, event_update_selected
):
    pass


@solara.component
def AlbumPanel(album, update_album_for_video):

    albums = [
        a.title
        for a in AlbumModel.select(AlbumModel.title).order_by(AlbumModel.title.asc())
    ]

    solara.Text(f"{album} current Album")
    if album.value == "":
        with solara.Row(justify="center"):
            solara.Select(
                label="Album",
                value=album,
                values=albums,
                on_value=update_album_for_video,
            )
        with solara.Link(f"/api/albums/"):
            solara.Button(f"Album Table", classes=["button"])

    else:
        _album = Album.get_by(title=album.value)
        if _album is None:
            solara.Error(f"_album is None!!!!!")
            return
        with solara.Link(f"/api/albums/details/{_album.instance.id}"):
            solara.Button(f"{album}", classes=["button"])


@solara.component
def Page():
    router = solara.use_router()

    # if "current_user" in session:
    #     logger.debug(session["current_user"])
    # else:
    #     logger.debug(f"No user currently logged in")
    #     with solara.Error(f"No user currently logged in"):
    #         with solara.Link("/"):
    #             solara.Button("Home", classes=["button"])
    #     return
    video_id = parse_url_args()
    try:
        video = Video(video_id)
    except Exception as e:
        logger.error(f"Exception {e}")
        with solara.Error(f"Video Id {video_id} not found."):
            with solara.Link("/"):
                solara.Button("Home", classes=["button"])
        return

    def download_video():
        results = download_video_file(
            video.instance.youtube_id, WORKING / video.instance.youtube_id
        )
        video.add_file(results[0])

    def download_info():
        info, files = get_video_info(video.instance.youtube_id)

    def update_selected(section):
        selected.set(section)

    def create_section(*args):
        start = args[0]["start"]
        end = args[0]["end"]
        logger.debug(f"Creating section from {start} to {end}")
        _section = Section.create(
            {
                "start": start,
                "end": end,
                "section_type": "instrumental",
                "video_id": video.instance.id,
            }
        )

        sections.set(sections.value + [_section.serialize()])
        logger.debug(f"After Creating section from {start} to {end}")

    def remove_section(section):
        _sect = Section.get_by(id=section["id"])
        logger.debug(f"Remove section {_sect}")
        _sect.delete()
        a = []
        a[:] = [d for d in sections.value if d.get("id") != section["id"]]
        sections.set(a)

    dv = DiscVideoModel.select().where(DiscVideoModel.video == video.instance).first()
    if dv is None:
        _album_title = ""
    else:
        _album_title = dv.disc.album.title
    current_album_title = solara.use_reactive(_album_title)

    def update_album_for_video(album_title):
        _album = Album.get_by(title=album_title)
        _album.add_video(video=video.instance)
        current_album_title.set(_album.instance.title)

        logger.debug(f"Updating Album For video {album_title}")

    with solara.Column(classes=["main-container"]):
        with solara.Row():
            with solara.Columns([8, 4]):
                with solara.Card():
                    VideoInfoPanel(video=video.instance)
                with solara.Card():
                    AlbumPanel(
                        album=current_album_title,
                        update_album_for_video=update_album_for_video,
                    )

        with solara.lab.Tabs():
            # with solara.lab.Tab("Sectionalizer"):
            #     Sectionalizer(video=video, create_section=create_section)
            with solara.lab.Tab("Sections"):
                if len(sections.value) > 0:
                    with solara.Column():
                        SectionSelector(
                            sections=sections.value,
                            selected=selected.value,
                            video_duration=video.instance.duration * 1000,
                            event_create_section=create_section,
                            event_update_selected=update_selected,
                            event_remove_section=remove_section,
                        )
            with solara.lab.Tab("Files"):
                for file in video.file_repo.my_files(video.instance.id):
                    solara.Markdown(f"### {file['file']}")
                with solara.Column():
                    solara.Button(
                        f"Download Info", on_click=download_info, classes=["button"]
                    )
                    solara.Button(
                        f"Download Video", on_click=download_video, classes=["button"]
                    )
                    solara.Button(f"Create/Download Audio", classes=["button"])
