from pathlib import Path

import peewee
import solara
import solara.lab
from loguru import logger
from solara.lab import task

from hmtc.models import Channel, Playlist, Series, Video
from hmtc.utils.general import time_since_update

all_series = [s.name for s in Series.select()]
all_channels = [c.name for c in Channel.select()]
if all_series == []:
    all_series = ["No Series"]
if all_channels == []:
    all_channels = ["No Channels"]

name = solara.reactive("")
url = solara.reactive("http://www.youtube.com")

series = solara.reactive(all_series[0])
enabled = solara.reactive(True)
album_per_episode = solara.reactive(False)
channel = solara.reactive(all_channels[0])
add_videos_enabled = solara.reactive(True)


def add_new_playlist():
    try:
        playlist = Playlist.create(
            title="New Playlist",
            url="http://www.youtube.com",
            series=Series.get_or_none(),
            channel=Channel.get_or_none(),
        )
        logger.debug(f"Created new playlist: {playlist.title}")
    except peewee.IntegrityError:
        logger.debug("Playlist already exists")
        return


def save_playlist(playlist):
    if playlist is None:
        logger.error("Playlist not found")
        return
    if not name == "":
        playlist.title = name.value
        playlist.url = url.value
        playlist.series = Series.get(Series.name == series.value)
        playlist.enabled = enabled.value
        playlist.album_per_episode = album_per_episode.value
        playlist.channel = Channel.get(Channel.name == channel.value)
        playlist.enable_video_downloads = add_videos_enabled.value
        playlist.save()
        logger.debug("Updated playlist name")


def PlaylistDetail(playlist_id):
    updating = solara.use_reactive(False)

    @task
    def update():
        logger.debug(f"Updating playlist {playlist.title}")
        updating.set(True)
        playlist.check_for_new_videos()
        updating.set(False)
        logger.success(f"Updated database from Playlist {playlist.title}")

    if playlist_id is None:
        logger.debug("Playlist not found")
        return

    playlist = Playlist.select().where(Playlist.id == playlist_id).get()
    name.set(playlist.title)
    url.set(playlist.url)
    # series.set(playlist.series.name)
    if playlist.channel is not None:
        channel.set(playlist.channel.name)

    def update_playlist():
        save_playlist(playlist)

    def update_my_videos():
        playlist.update_videos_with_playlist_info()

    with solara.Column():
        solara.InputText(label="Name", value=name, continuous_update=False)
        if playlist.poster is not None:
            solara.Image(image=playlist.poster, width="400px")
        solara.InputText(label="URL", value=url, continuous_update=False)
        solara.Markdown(f"Number of of Videos: {playlist.videos.count()}")
        solara.Select(label="Series", value=series, values=all_series)
        solara.Select(label="Channel", value=channel, values=all_channels)
        solara.Checkbox(label="Enabled", value=enabled)
        solara.Checkbox(label="Add Videos Enabled", value=add_videos_enabled)

        with solara.Card():
            solara.Button(label="Save", on_click=update_playlist)
            solara.Button(label="Refresh videos info from Youtube", on_click=update)
            solara.Button(
                label="Apply Playlist properties to its videos",
                on_click=update_my_videos,
            )


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()
    # selected_series = solara.use_reactive(Series.select())

    if len(router.parts) == 1:
        solara.Markdown("No Playlist Selected")
        return
    playlist_id = router.parts[level:][0]
    if playlist_id.isdigit():
        PlaylistDetail(playlist_id)
