from pathlib import Path

import PIL
import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Album as AlbumModel
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import FileManager
from hmtc.utils.opencv.image_manager import ImageManager


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        # 10/26/24 - not sure what this is doing
        return None

    return router.parts[level:][0]


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    album_id = parse_url_args()
    if album_id is None:
        with solara.Error():
            solara.Markdown("No album ID found in URL.")
        return
    try:
        album = AlbumItem.get_details_for_album_id(album_id=album_id)
    except Exception as e:
        with solara.Error():
            solara.Markdown(f"Error loading album with ID {album_id}.")
            solara.Markdown(f"Error: {e}")
        return
    with solara.Columns([6, 6]):
        with solara.Column():
            poster = FileManager.get_file_for_album(album=album, filetype="poster")
            image = ImageManager(poster).image
            solara.Image(image, width="400")
            solara.Markdown(f"Album Title: {album.title}")
        with solara.Column():
            solara.Markdown(f"Album ID: {album.id}")
            solara.Markdown(f"Release Date: {album.release_date}")
    with solara.Info(label="Videos"):
        for video in album.videos:
            with solara.Row():

                solara.Markdown(f"{video.title}")
                solara.Button(
                    "Use Album Art",
                    on_click=lambda: album.use_video_poster(video=video),
                )
                with solara.Link(f"/video-details/{video.id}"):
                    solara.Markdown("Details")
    with solara.Info(label="Tracks"):
        for track in album.tracks:
            solara.Markdown(f"{track.title}")
