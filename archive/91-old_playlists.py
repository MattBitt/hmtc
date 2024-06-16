from datetime import datetime

import solara
import solara.lab
from loguru import logger

from hmtc.models import Playlist, Series

adding_mode = solara.reactive(False)


def get_playlists():
    query = Playlist.select().join(Series).order_by(Series).order_by(Playlist.title)
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
        return str("Just now")


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
        PlaylistCardBody(playlist, editing=editing)
        PlaylistCardControlPanel(
            editing=editing,
            set_editing=set_editing,
            set_updating=set_updating,
        )
        PlaylistCardStatusBar(status_bar_text)


@solara.component
def AddPlaylistCard():
    with solara.Card():
        if adding_mode.value is True:
            logger.debug("Adding Playlist")
            solara.InputText("Playlist Name", value="")
            solara.InputText("Series Name", value="")
            solara.InputText("Album Per Episode", value="")
            solara.Button(
                "Save Playlist",
                on_click=lambda: logger.debug("Save Playlist"),
            )
            solara.Button("Cancel", on_click=adding_mode.set(False))
        else:
            solara.Button("Add Playlist", on_click=adding_mode.set(True))


@solara.component
def PlaylistsGroup():
    AddPlaylistCard()


@solara.component
def Page():
    PlaylistsGroup()
