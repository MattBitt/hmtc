import solara
from loguru import logger
from hmtc.models import Album as AlbumTable

from hmtc.mods.album import Album


@solara.component
def AlbumInfo(video):

    album = solara.reactive(None)
    album.set(Album.grab_for_video(video.id))

    def delete_album():
        album.value.delete_album()
        album.set(None)

    def create_album():
        Album.create_for_video(video)
        album.set(Album.grab_for_video(video.id))

    def update_album():
        logger.debug("Updating Album")
        Album.update_album(title=album.value.title, video_id=video.id)

    if album.value is not None:
        with solara.Row():
            solara.InputText(
                label="Album Title",
                value=album.value.title,
                on_value=lambda x: album.set(
                    Album(title=x, video_id=video.id, tracks=[])
                ),
            )
            solara.Button(
                label="Save Album",
                on_click=update_album,
            )
            solara.Button(
                "Delete Album",
                on_click=delete_album,
            )
    else:
        solara.Button(
            "Create Album",
            on_click=create_album,
        )
