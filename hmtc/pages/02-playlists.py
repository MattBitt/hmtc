import solara
import solara.lab
from solara.alias import rv
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Playlist, Video, Series
from datetime import datetime, timedelta
from loguru import logger


def get_playlists():
    query = Playlist.select().join(Series).order_by(Series).order_by(Playlist.name)
    return query


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
        return str(f"Just now")


@solara.component
def PlaylistButton():
    with solara.Row():
        solara.Button(
            "Add playlist",
            on_click=lambda: logger.debug("Add playlist"),
            classes=[],
        )


@solara.component
def PlaylistCardHeader(playlist):
    with solara.Div(classes=["card-header"]):
        solara.Markdown(playlist.name)


@solara.component
def BodyDisplay(playlist):
    solara.Markdown(f"#### Series: {playlist.series.name}")
    solara.Markdown(f"#### APE: {playlist.album_per_episode}")
    solara.Markdown(f"#### {len(playlist.videos)} videos")


@solara.component
def BodyEdit(playlist):
    solara.InputText("Name", value=playlist.name, classes=["input1"])
    solara.InputText(
        "Last Updated",
        value=playlist.last_update_completed,
        classes=["input2"],
    )
    solara.InputText("Series Name", value=playlist.series.name)
    solara.InputText("Separate APE?", value=playlist.album_per_episode)


@solara.component
def PlaylistCardBody(playlist, editing):
    with solara.Column(classes=["card-body"]):
        if editing:
            BodyEdit(playlist)
        else:
            BodyDisplay(playlist)


@solara.component
def PlaylistCardImage(editing):
    url = "data:image/jpeg;base64,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"

    with solara.Div():
        rv.Img(src=url, contain=True, max_height="300px")


@solara.component
def PlaylistCardControlPanel(editing, set_editing, set_updating):
    # not sure if this is the best way to do this
    # need to figure out how to pass the playlist object
    # from the on_click event without 'calling' the
    # function

    with solara.Row(gap="10px", justify="center"):
        solara.Button(
            "Edit Playlist" if not editing else "Cancel",
            on_click=lambda: set_editing(not editing),
            classes=[],
        )

        solara.Button(
            "Update playlist",
            on_click=lambda: set_updating(True),
            classes=[],
        )


@solara.component
def PlaylistCardStatusBar(status_bar_text):
    with solara.Column(align="center", classes=["footer"]):
        solara.Text(status_bar_text)


@solara.component
def PlaylistCard(playlist):
    updated, set_updated = solara.use_state(False)
    updating, set_updating = solara.use_state(False)
    since_updated, set_since_updated = solara.use_state(time_since_update(playlist))
    editing, set_editing = solara.use_state(False)
    status_bar_text = solara.use_reactive("")

    def refresh_playlist(playlist):
        logger.debug(f"💥💥💥 Running update_playlist_videos for {playlist.name}")
        set_updating(True)
        playlist.check_for_new_videos()
        set_updated(True)
        set_updating(False)

    if editing:
        status_bar_text = f"Editing {playlist.name} Playlist"
    elif updating:
        # not sure why this doesn't update the status bar
        status_bar_text = f"Updating {playlist.name} Playlist"
        logger.debug(f"🏠🏠🏠Updating {playlist.name} Playlist")
        refresh_playlist(playlist)
    else:
        status_bar_text = f"Last updated: {since_updated}"

    if updated:
        set_since_updated(time_since_update(playlist))
        set_updated(False)

    with solara.Card(classes=["playlist-card"]):
        PlaylistCardHeader(playlist)
        PlaylistCardImage(editing=editing)
        PlaylistCardBody(playlist, editing=editing)
        PlaylistCardControlPanel(
            editing=editing,
            set_editing=set_editing,
            set_updating=set_updating,
        )
        PlaylistCardStatusBar(status_bar_text)


@solara.component
def PlaylistsGroup():
    playlists, set_playlists = solara.use_state(None)
    loading, set_loading = solara.use_state(True)

    if loading:
        set_playlists(get_playlists())
        set_loading(False)

    else:
        with solara.ColumnsResponsive(12, large=[4, 4, 4]):
            for playlist in playlists:
                PlaylistCard(
                    playlist,
                )


@solara.component
def Page():

    MyAppBar()
    with solara.lab.Tabs():
        with solara.lab.Tab("Tab 1"):
            PlaylistsGroup()
        with solara.lab.Tab("Tab 2"):
            solara.Markdown("Pretend it's a different page")
            PlaylistsGroup()
            solara.Markdown("World")
