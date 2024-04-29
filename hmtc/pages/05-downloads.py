import solara
import solara.lab
from loguru import logger
from pathlib import Path
import json
from hmtc.pages import config
from hmtc.models import Playlist

downloads_path = config.get("GENERAL", "DOWNLOAD_PATH")
files = solara.reactive([])


def read_json_file(filename):
    with open(Path(downloads_path) / filename, "r") as f:
        data = json.load(f)
    return data


@solara.component
def FileCard(file, playlist_id=None):

    def add_file_to_playlist():
        logger.debug(f"Adding file {file} to playlist {playlist_id}")
        if file.suffix == ".json":
            data = read_json_file(file)
            logger.debug(f"Data: {data["title"]}")

        # playlist_name = f"Playlist {playlist_id}"
        playlist = Playlist.get_or_none(Playlist.youtube_id == playlist_id)
        if playlist:
            playlist.add_file(file)
            logger.success(f"Finished adding file {file} to playlist")
        # is_playlist_existing.set(True)

    with solara.Card():
        solara.Markdown(f"{file}")
       
        with solara.CardActions():
            solara.Button(
                "Add File to Playlist", on_click=add_file_to_playlist
            )
            solara.Button("Delete", on_click=lambda: logger.debug(f"Deleting file: {file}"))


@solara.component
def PlaylistFilesCard(playlist_id):
    is_playlist_existing = solara.use_reactive((False))
    playlist = Playlist.get_or_none(Playlist.youtube_id == playlist_id)
    if playlist:
        is_playlist_existing.set(True)
    
    if playlist is None:
        logger.debug(f"Playlist {playlist_id} not found in DB")
    
    playlist_files = list(Path(downloads_path).glob(f"{playlist_id}*"))

    def add_playlist_to_db():
        logger.debug(f"Need to add playlist {playlist_id}")
        for f in playlist_files:
            if f.suffix == ".json":
                data = read_json_file(f)
                # logger.debug(f"Data: {data['title']}")
                Playlist.create(youtube_id=playlist_id, name=data["title"], url=data['webpage_url'])
                is_playlist_existing.set(True)
    
    color = "yellow"
    if not is_playlist_existing.value:
        color = "red"
    
    with solara.Card(style={"background":color}):
        solara.Markdown(f"{playlist_id}")
        if is_playlist_existing.value:
            solara.Markdown(f"**{playlist.name}**")
        # solara.Markdown(f"Playlist already exists in DB?: {is_playlist_existing.value}")
        if is_playlist_existing.value:
            for file in playlist_files:
                FileCard(file, playlist_id=playlist_id)

            # with solara.CardActions():

            #     # solara.Button(
            #     #     "Delete",
            #     #     on_click=lambda: logger.debug(f"Deleting file: {playlist_id}"),
            #     # )
        else:
            solara.Button("Create Playlist and add Files to DB", on_click=add_playlist_to_db)


@solara.component
def Page():
    def clear_downloads():
        for f in files.value:
            logger.debug(f"Removing existing file in downloads: {f}")
            # f.unlink()

    def file_details(file):
        file = Path(file)
        if file.stem[:2] == "PL" and len(file.stem) > 33:
            p_id = file.stem[:34]
            # logger.debug(f" {p_id}")
            return "playlist"
        else:
            return None

            # logger.debug(f"Processing file: {f}")

    files.set(list(Path(downloads_path).glob("*")))
    with solara.Column():
        solara.Markdown("**Downloads** Page")
        solara.Markdown("Downloaded Files")
        solara.Button(
            "Refresh Downloads",
            on_click=lambda: files.set(list(Path(downloads_path).glob("*"))),
        )

        solara.Button("Clear Downloads", on_click=lambda: logger.debug("Clearing"))
        solara.Markdown(f"Found {len(files.value)} files in downloads folder")
        playlist_ids = set(
            [f.stem[:34] for f in files.value if file_details(f) == "playlist"]
        )
        solara.Markdown(f"{len(playlist_ids)} Playlists that have files in folder")
    
    with solara.ColumnsResponsive(4):
        for f in playlist_ids:
            if file_details(f) == "playlist":
                PlaylistFilesCard(f)
