from pathlib import Path

import PIL
import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Album as AlbumModel
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
        album = AlbumItem.load(album_id)
    except Exception as e:
        with solara.Error():
            solara.Markdown(f"Error loading album with ID {album_id}.")
            solara.Markdown(f"Error: {e}")
        return

    with solara.Columns([6, 6]):
        with solara.Column():
            # poster = FileManager.get_file_for_album(album=album, filetype="poster")
            # image = ImageManager(poster).image
            solara.Markdown(f"## Album Poster:")
            # solara.Image(image, width="400")
            solara.Markdown(f"Album Title: {album.title}")
        with solara.Column():
            solara.Markdown(f"Album ID: {album.id}")
            solara.Markdown(f"Release Date: {album.release_date}")
    with solara.Info(label="Videos"):
        album_vids = AlbumItem.get_videos(album_id=album.id)
        for video in album_vids:
            with solara.Row():
                solara.Markdown(f"{video.title}")
                with solara.Link(f"/api/videos/details/{video.id}"):
                    solara.Markdown("Details")
