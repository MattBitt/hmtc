from pathlib import Path

import solara
import solara.lab
from flask import session
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.transitions.swap import SwapTransition
from hmtc.components.video.video_info_panel import VideoInfoPanel
from hmtc.config import init_config
from hmtc.domains.album import Album
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.utils.youtube_functions import download_video_file, get_video_info

config = init_config()
WORKING = config["WORKING"]


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")

    try:
        video = Video(_id)

    except Exception as e:
        logger.error(f"Exception {e}")

    return video


def download_video(video: Video):
    results = download_video_file(
        video.instance.youtube_id, WORKING / video.instance.youtube_id
    )
    video.add_file(results[0])


def download_info(video: Video):
    info, files = get_video_info(video.instance.youtube_id)


sections = solara.reactive([])
selected = solara.reactive({})
refresh_counter = solara.reactive(1)


@solara.component
def NoAlbum(video, choosing_disc):
    album_title = solara.use_reactive("")
    albums = [
        a.title
        for a in AlbumModel.select(AlbumModel.title).order_by(AlbumModel.title.asc())
    ]
    reactive_disc = solara.use_reactive(None)

    def update_album_for_video(disc_folder_name):
        from hmtc.domains.disc import Disc

        logger.debug(f"{disc_folder_name}")
        _album = Album.get_by(title=album_title.value)
        if disc_folder_name == "Create New":
            _album.add_video(video=video.instance)
        else:
            _disc = Disc.get_by(folder_name=disc_folder_name)
            _album.add_video(video=video.instance, existing_disc=_disc.instance)
        # disc.set(_disc)
        #        album.set(_album)
        choosing_disc.set(False)
        refresh_counter.set(refresh_counter.value + 1)

    def choose_disc(disc_title):
        choosing_disc.set(True)

    def cancel():
        choosing_disc.set(False)
        refresh_counter.set(refresh_counter.value + 1)

    with solara.Row(justify="center"):
        solara.Select(
            label="Album",
            value=album_title,
            values=albums,
            on_value=choose_disc,
        )
    new_item = ["Create New"]
    if choosing_disc.value is True:
        _album = Album.get_by(title=album_title.value)
        if _album is None:
            logger.error(f"{_album} is None for {album_title.value}")
            return
        discs = (
            DiscModel.select()
            .where(DiscModel.album_id == _album.instance.id)
            .order_by(DiscModel.folder_name.asc())
        )
        if len(discs) == 0:
            solara.Button(
                label="Create Disc",
                icon_name=Icons.DISC.value,
                on_click=lambda: update_album_for_video(new_item[0]),
                classes=["button"],
            )
        else:

            _disc_list = new_item + [disc.folder_name for disc in discs]
            solara.Select(
                label="Which Disc?",
                value=reactive_disc,
                values=_disc_list,
                on_value=update_album_for_video,
            )
        solara.Button(label="Cancel", classes=["button mywarning"], on_click=cancel)


@solara.component
def HasAlbum(album, video):
    if album.value is None:
        logger.error("Album is None here....")
        return
    _album = Album.get_by(title=album.value.instance.title)
    if _album is None:
        solara.Error(f"_album is None!!!!!")
        return
    with solara.Link(f"/api/albums/details/{_album.instance.id}"):
        solara.Button(
            label=f"{album.value.instance.title}",
            classes=["button"],
            icon_name=Icons.ALBUM.value,
        )


@solara.component
def AlbumPanel(album, video):
    choosing_disc = solara.use_reactive(False)

    with SwapTransition(show_first=(album.value is None), name="fade"):
        NoAlbum(video=video, choosing_disc=choosing_disc)
        HasAlbum(album=album, video=video)


@solara.component
def SelectedSectionPanel(sections):
    if len(sections.value) > 0:
        if selected.value == {}:
            solara.Text(f"Nothing Selected")
        else:
            solara.Text(f"Current Section {sections.value[selected.value]}")
    else:
        solara.Text(f"No Sections")


@solara.component
def NoVideoError():
    with solara.Error(f"Video Id not found."):
        with solara.Link("/"):
            solara.Button("Home", classes=["button"])


@solara.component
def FilesPanel(video: Video):
    with solara.Column():
        for file in video.file_repo.my_files(video.instance.id):
            with solara.Row():
                solara.Markdown(f"### {file['file']}")
        with solara.Row():
            solara.Button(
                f"Download Info",
                on_click=lambda: download_info(video),
                classes=["button"],
            )
            solara.Button(
                f"Download Video",
                on_click=lambda: download_video(video),
                classes=["button"],
            )
        solara.Button(f"Create/Download Audio", classes=["button"])


@solara.component
def Tabs(selected, video, sections):
    with solara.lab.Tabs():
        with solara.lab.Tab("Sections"):
            with solara.Column():
                with solara.Card():
                    solara.Markdown(f"{len(sections.value)} sections - Summary Panel")

        with solara.lab.Tab("Files"):
            with solara.Column():
                FilesPanel(video)


@solara.component
def TopRow(video, sections, album):
    with solara.Row():
        with solara.Columns([8, 4]):
            with solara.Card():
                VideoInfoPanel(video_domain=video)
            with solara.Column():
                with solara.Card():
                    AlbumPanel(
                        album=album,
                        video=video,
                    )
                with solara.Card():
                    SelectedSectionPanel(sections=sections)


@solara.component
def Page():
    router = solara.use_router()
    selected = solara.use_reactive(0)
    # if "current_user" in session:
    #     logger.debug(session["current_user"])
    # else:
    #     logger.debug(f"No user currently logged in")
    #     with solara.Error(f"No user currently logged in"):
    #         with solara.Link("/"):
    #             solara.Button("Home", classes=["button"])
    #     return
    video = parse_url_args()

    if refresh_counter.value > 0:
        with solara.Column(classes=["main-container"]):
            if video is None:
                NoVideoError()
            else:
                sections = solara.use_reactive(
                    [Section(s).serialize() for s in video.sections()]
                )
                album = solara.use_reactive(video.album())
                TopRow(video, sections, album)
                Tabs(selected, video, sections)
