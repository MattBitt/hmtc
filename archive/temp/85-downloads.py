from pathlib import Path

import solara
import solara.lab
from loguru import logger

from hmtc.components.my_app_bar import MyAppBar
from hmtc.config import init_config
from hmtc.models import Channel, Playlist, Series, Video
from hmtc.utils.general import determine_file_object_association, read_json_file

config = init_config()
downloads_path = Path(config["paths"]["working"]) / "downloads"
env = config["general"]["environment"]
files = solara.reactive([])


@solara.component
def SeriesFileCard(file):
    existing_series = [s.name for s in Series.select()]

    def delete_file():
        try:
            (Path(downloads_path) / file).unlink()
            logger.success(f"Deleted file: {file}")
        except Exception as e:
            logger.error(f"Error deleting file: {file}, {e}")

    with open(Path(downloads_path) / file, "r") as f:
        data = f.readlines()

    def add_all_series_to_db():
        logger.debug(f"Adding all series in {file} to DB")
        for d in data:
            if d.strip() not in existing_series:
                Series.create(name=d.strip())
                logger.success(f"Added series {d.strip()} to DB")
            else:
                logger.debug(f"Series {d.strip()} already in DB")

    with solara.Card():
        solara.Markdown(f"Series File: {file}")
        for d in data:
            if d.strip() in existing_series:
                solara.Markdown(f"**{d.strip()}**")
            else:
                solara.Markdown(d)
        with solara.CardActions():
            solara.Button("Add All Series to DB", on_click=add_all_series_to_db)
            solara.Button("Delete", on_click=delete_file)


@solara.component
def ChannelFilesCard(file, data):
    channel_yt_id = data["channel_id"]

    def add_file_to_channel():
        logger.debug(f"Adding file {file} to channel {channel_yt_id}")
        if file.suffix == ".json":
            p = Path(downloads_path) / file
            if not p.exists():
                logger.error(f"File {file} does not exist")
                return

            data = read_json_file(Path(downloads_path) / file)
            logger.debug(f"Data: {data["title"]}")

        # channel_name = f"Channel {channel_id}"
        channel = Channel.get_or_none(Channel.youtube_id == channel_yt_id)
        if channel:
            channel.add_file(file)
            logger.success(f"Finished adding file {file} to channel")
        # is_channel_existing.set(True)

    with solara.Card():
        solara.Markdown(f"{file}")

        with solara.CardActions():
            solara.Button("Add File to Channel", on_click=add_file_to_channel)
            solara.Button(
                "Delete", on_click=lambda: logger.debug(f"Deleting file: {file}")
            )


@solara.component
def VideoFilesCard(file, data):
    video_yt_id = data["id"]
    video = Video.get_or_none(Video.youtube_id == video_yt_id)
    color = "orange"
    if video is not None:
        color = "purple"

    def add_file_to_video():
        logger.debug(f"Adding file {file} to video {video_yt_id}")
        # if file.suffix == ".json":
        #     p = Path(downloads_path) / file
        #     if not p.exists():
        #         logger.error(f"File {file} does not exist")
        #         return

        #     data = read_json_file(Path(downloads_path) / file)
        #     logger.debug(f"Data: {data["title"]}")
        # elif file.suffix in [".jpg", ".jpeg", ".png", ".vtt"]:
        video = Video.get_or_none(Video.youtube_id == video_yt_id)
        if video:
            video.add_file(file)
            logger.success(f"Finished adding file {file} to video")
            # is_video_existing.set(True)

    with solara.Card(style={"background": color}):
        solara.Markdown(f"{file}")

        with solara.CardActions():
            solara.Button(
                "Add File to Video",
                on_click=add_file_to_video,
                disabled=(color == "orange"),
            )
            solara.Button(
                "Delete", on_click=lambda: logger.debug(f"Deleting file: {file}")
            )


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
            solara.Button("Add File to Playlist", on_click=add_file_to_playlist)
            solara.Button(
                "Delete", on_click=lambda: logger.debug(f"Deleting file: {file}")
            )


@solara.component
def UnknownFilesCard(file, data):
    def delete_file():
        try:
            (Path(downloads_path) / file).unlink()
            logger.success(f"Deleted file: {file}")
        except Exception as e:
            logger.error(f"Error deleting file: {file}, {e}")

    file = file if isinstance(file, str) else file.name
    if not data:
        data = {}

    with solara.Card():
        solara.Markdown(f"Unknown File: {file}")
        solara.Markdown(f"Unknown Data: {data}")
        with solara.CardActions():
            solara.Button("Delete", on_click=delete_file)


@solara.component
def PlaylistFilesCard(file, data):
    is_playlist_existing = solara.use_reactive((False))
    playlist_id = data["id"]

    def add_playlist_to_db():
        logger.debug(f"Need to add playlist {playlist_id}")
        for f in playlist_files:
            if f.suffix == ".json":
                data = read_json_file(f)
                # logger.debug(f"Data: {data['title']}")
                channel = Channel.get_or_none(Channel.youtube_id == data["channel_id"])
                if channel:
                    if data["channel_id"] == "UCcnAEyz9VnlBL1DiQqliJkQ":
                        if playlist_id == "PLVuktCy_G9zLqq_g0D44cKCE0xEmenRUQ":
                            data["title"] = "Behind the Bars Clips"

                    Playlist.create(
                        youtube_id=playlist_id,
                        name=data["title"],
                        url=data["webpage_url"],
                        channel=channel,
                    )
                    is_playlist_existing.set(True)

    playlist = Playlist.get_or_none(Playlist.youtube_id == playlist_id)
    if playlist:
        is_playlist_existing.set(True)

    playlist_files = list(Path(downloads_path).glob(f"{playlist_id}*"))

    color = "yellow"
    if not is_playlist_existing.value:
        color = "red"

    with solara.Card(style={"background": color}):
        solara.Markdown(f"{playlist_id}")
        if is_playlist_existing.value and playlist is not None:
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
            solara.Button(
                "Create Playlist and add Files to DB", on_click=add_playlist_to_db
            )


@solara.component
def ChannelCard(f, data):
    is_channel_existing = solara.use_reactive((False))

    channel_yt_id = data["channel_id"]
    channel_name = data["title"]
    channel_url = data["webpage_url"]

    channel = Channel.get_or_none(Channel.youtube_id == channel_yt_id)

    if channel:
        is_channel_existing.set(True)

    else:
        logger.debug(f"Channel {channel_yt_id} not found in DB")

    def add_channel_to_db():
        logger.debug(f"Adding channel {channel_yt_id}")
        Channel.create(youtube_id=channel_yt_id, name=channel_name, url=channel_url)
        is_channel_existing.set(True)

    color = "pink"
    if not is_channel_existing.value:
        color = "blue"

    with solara.Card(style={"background": color}):
        solara.Markdown(f"{channel_yt_id}")
        if is_channel_existing.value:
            solara.Markdown(f"**{channel.name}**")
            solara.Markdown("Existing Files:")
            for cf in channel.files:
                solara.Markdown(f"{cf.file.filename}")

            with solara.Column():
                for f in files.value:
                    ftype, new_data = determine_file_object_association(f)
                    if ftype == "channel" and new_data["channel_id"] == channel_yt_id:
                        ChannelFilesCard(f, new_data)

        # solara.Markdown(f"Channel already exists in DB?: {is_channel_existing.value}")

        else:
            solara.Button(
                "Create Channel and add Files to DB", on_click=add_channel_to_db
            )


@solara.component
def Page():
    def clear_downloads():
        for f in files.value:
            logger.debug(f"Removing existing file in downloads: {f}")
            # f.unlink()

            # logger.debug(f"Processing file: {f}")

    files.set([file for file in Path(downloads_path).glob("**/*") if file.is_file()])
    with solara.Column():
        solara.Markdown("**Downloads** Page")
        solara.Markdown("Downloaded Files")
        solara.Button(
            "Refresh Downloads",
            on_click=lambda: files.set(list(Path(downloads_path).glob("*"))),
        )

        solara.Button("Clear Downloads", on_click=lambda: logger.debug("Clearing"))
        solara.Markdown(f"Found {len(files.value)} files in downloads folder")
        # playlist_ids = set(
        #     [f.stem[:34] for f in files.value if determine_file_type(f) == "playlist"]
        # )
        # solara.Markdown(f"{len(playlist_ids)} Playlists that have files in folder")
    MyAppBar(env)

    channel_files = []
    playlist_files = []
    video_files = []
    bad_videos = []  # problem with youtube id in name
    for f in files.value:
        ftype, data = determine_file_object_association(f)
        if not ftype or not data:
            UnknownFilesCard(f, data)
        else:
            match ftype:
                case "playlist":
                    if "dummy" in data:
                        playlist_files.append({"file": f, "data": {"id": f.stem[:34]}})
                    else:
                        playlist_files.append({"file": f, "data": data})
                case "channel":
                    channel_files.append({"file": f, "data": data})
                case "video":
                    video_files.append({"file": f, "data": data})
                case "series":
                    SeriesFileCard(f)
                case "bad video":
                    bad_videos.append({"file": f, "data": data})
                case _:
                    logger.debug(f"Unknown file type: {f}")
                    logger.debug(f"ftype: {ftype}")

                    logger.debug(f"Data: {data}")
    with solara.Card():
        solara.Markdown("Totals")
        solara.Markdown(f"Channels: {len(channel_files)}")
        solara.Markdown(f"Playlists: {len(playlist_files)}")
        solara.Markdown(f"Videos: {len(video_files)}")
        solara.Markdown(f"Bad Videos: {len(bad_videos)}")

    with solara.ColumnsResponsive(4):
        for bad_video in bad_videos[:10]:
            with solara.Card():
                solara.Markdown("Bad Video")
                UnknownFilesCard(bad_video["file"], bad_video["data"])

        for channel in channel_files[:10]:
            with solara.Card():
                solara.Markdown("Channel with Files to Import")
                ChannelCard(channel["file"], channel["data"])

        for playlist in playlist_files[:10]:
            with solara.Card():
                solara.Markdown("Playlist with Files to Import")
                PlaylistFilesCard(playlist["file"], playlist["data"])

        for video in video_files[:10]:
            with solara.Card():
                solara.Markdown("Video with Files to Import")
                VideoFilesCard(video["file"], video["data"])
