import peewee
import solara
import solara.lab
from loguru import logger
from solara.lab import task

from hmtc.models import Channel, Playlist, Series
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


@solara.component
def PlaylistCard(playlist):
    updating = solara.use_reactive(False)
    if playlist is None:
        logger.debug("Playlist not found")
        return

    @task
    def update():

        logger.debug(f"Updating playlist {playlist.title}")
        updating.set(True)
        # time.sleep(3)
        playlist.check_for_new_videos()
        updating.set(False)
        logger.success(f"Updated database from Playlist {playlist.title}")

    @task
    def load_info():
        logger.debug(f"Loading info for {playlist.title}")
        updating.set(True)
        playlist.load_info()
        updating.set(False)
        logger.success(f"Loaded info for Playlist {playlist.title}")

    with solara.Card():
        if updating.value is False:
            solara.Markdown(playlist.title)
            if playlist.poster is not None:
                solara.Image(playlist.poster, width="200px")
            solara.Markdown(f"Videos in DB: {playlist.videos.count()}")

            solara.Markdown(f"URL: {playlist.url}")
            solara.Markdown(f"Last Updated: {time_since_update(playlist)}")
            solara.Markdown(
                f"New Video Status: {'Enabled' if playlist.enable_video_downloads else 'Disabled'} "
            )
            with solara.CardActions():
                with solara.Link(f"/playlist-detail/{playlist.id}"):
                    solara.Button("Edit", on_click=lambda: logger.debug("Edit"))
                solara.Button("Delete", on_click=lambda: logger.debug("Delete"))

        else:
            solara.SpinnerSolara()


@solara.component
def Page():
    def update_my_videos():
        for playlist in Playlist.select():
            playlist.update_videos_with_playlist_info()

    with solara.ColumnsResponsive(
        12,
        large=3,
    ):
        for playlist in Playlist.select().order_by(Playlist.updated_at.desc()):
            PlaylistCard(playlist)
    solara.Button("Add New Playlist", on_click=add_new_playlist)
    solara.Button(
        "Update all Videos with properties of their respective playlists",
        on_click=update_my_videos,
    )
