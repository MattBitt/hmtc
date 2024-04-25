import solara
import solara.lab
import peewee
from hmtc.models import Playlist, Series, Channel
from datetime import datetime
from loguru import logger
from solara.lab import task

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


def time_since_update(playlist):
    if not playlist.last_update_completed:
        return "Never"

    t = datetime.now() - playlist.last_update_completed

    if t.seconds > (24 * 3600):
        return str(f"{t.days} days ago")
    elif t.seconds > 3600:
        return str(f"{t.seconds // 3600} hours ago")
    elif t.seconds < 3600 and t.seconds > 60:
        return str(f"{(t.seconds // 60)} minutes ago")
    else:
        return str("Just now")


def add_new_playlist():
    try:
        playlist = Playlist.create(
            name="New Playlist",
            url="http://www.youtube.com",
            series=Series.get(),
            channel=Channel.get(),
        )
        logger.debug(f"Created new playlist: {playlist.name}")
    except peewee.IntegrityError:
        logger.debug("Playlist already exists")
        return


def save_playlist(playlist):
    if playlist is None:
        logger.error("Playlist not found")
        return
    if not name == "":
        playlist.name = name.value
        playlist.url = url.value
        playlist.series = Series.get(Series.name == series.value)
        playlist.enabled = enabled.value
        playlist.album_per_episode = album_per_episode.value
        playlist.channel = Channel.get(Channel.name == channel.value)
        playlist.add_videos_enabled = add_videos_enabled.value
        playlist.save()
        logger.debug("Updated playlist name")


def PlaylistDetail(playlist_id):
    playlist = Playlist.select().where(Playlist.id == playlist_id).get()
    name.set(playlist.name)
    url.set(playlist.url)
    series.set(playlist.series.name)
    channel.set(playlist.channel.name)

    def update_playlist():
        save_playlist(playlist)

    with solara.Card():
        solara.InputText(label="Name", value=name, continuous_update=False)
        solara.InputText(label="URL", value=url, continuous_update=False)
        solara.Select(label="Series", value=series, values=all_series)
        solara.Select(label="Channel", value=channel, values=all_channels)
        solara.Checkbox(label="Enabled", value=enabled)
        solara.Checkbox(label="Add Videos Enabled", value=add_videos_enabled)

        with solara.CardActions():
            solara.Button(label="Save", on_click=update_playlist)


#       solara.Markdown(f"URL: {playlist.url}")
#        solara.Markdown(f"Series: {playlist.series.name}")


@solara.component
def PlaylistCard(playlist):
    updating = solara.use_reactive(False)

    @task
    def update():

        logger.debug(f"Updating playlist {playlist.name}")
        updating.set(True)
        # time.sleep(3)
        playlist.check_for_new_videos()
        updating.set(False)
        logger.success(f"Updated database from Playlist {playlist.name}")

    with solara.Card():
        if updating.value is False:
            solara.Markdown(playlist.name)
            solara.Markdown(f"Videos in DB: {playlist.videos.count()}")

            solara.Markdown(f"Channel: {playlist.channel.name}")
            solara.Markdown(f"Series: {playlist.series.name}")
            solara.Markdown(f"URL: {playlist.url}")
            solara.Markdown(f"Last Updated: {time_since_update(playlist)}")
            solara.Markdown(
                f"New Video Status: {'Enabled' if playlist.add_videos_enabled else 'Disabled'} "
            )
            with solara.CardActions():
                with solara.Link(f"/playlists/{playlist.id}"):
                    solara.Button("Edit", on_click=lambda: logger.debug("Edit"))
                solara.Button("Delete", on_click=lambda: logger.debug("Delete"))
                solara.Button(label="Update", on_click=update)
        else:
            solara.SpinnerSolara()


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()
    # selected_series = solara.use_reactive(Series.select())

    def update():
        logger.debug("Updating")
        for p in Playlist.select().where(Playlist.enabled == True):
            p.check_for_new_videos()
        logger.success("Updated all playlists")

    if router.parts[-1] == "playlists":
        solara.Button("Add New Playlist", on_click=add_new_playlist)
        solara.Button("Update All Playlists", on_click=update)
        with solara.ColumnsResponsive(
            12,
            large=3,
        ):
            for playlist in Playlist.select().order_by(Playlist.updated_at.desc()):
                PlaylistCard(playlist)

    else:

        playlist_id = router.parts[level:][0]
        PlaylistDetail(playlist_id)
