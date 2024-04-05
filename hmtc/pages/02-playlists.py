import solara
import solara.lab
from archive.sol import sidebar, main_content
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Playlist, Video, Series
from pathlib import Path
from typing import Callable

# from hmtc.main import update_playlist
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger


# @solara.component_vue("mycard2.vue")
# def MyCard(
#     event_goto_report: Callable[[dict], None],
#     value=[1, 10, 30, 20, 3],
#     caption="My Card",
#     color="red",
#     dialog=False,
# ):
#     pass


def get_playlists(series=None):
    query = Playlist.select().join(Series).order_by(Series).order_by(Playlist.name)
    if series:
        query = query.where(Playlist.series == series)
        logger.debug(f"🔵🔵🔵 Series = {series.name}")
    else:
        logger.error("💡💡💡💡No series found")
    return query


def get_series():
    query = Series.select()
    return query


# def update(pl):
#     logger.debug(f"Updating playlist {pl.name}")
#     pl.check_for_new_videos()


@solara.component
def PlaylistButton():
    with solara.Row(justify="center"):
        solara.Button(
            "Add playlist",
            on_click=lambda: logger.debug("Add playlist"),
            classes=["mybutton"],
        )


@solara.component
def PlaylistCard(playlist, loading, set_loading, updated, set_updated):
    logger.debug(
        f"🥝🥝🥝Inside Playlist card playlist id = {playlist.id}, {loading}, {playlist.last_update_completed}"
    )

    def update_playlist_videos(playlist):
        logger.debug(f"💥💥💥 Running update_playlist_videos for {playlist.name}")
        set_loading(True)
        playlist.check_for_new_videos()
        set_updated(True)
        set_loading(False)

    def edit_playlist(playlist):
        logger.debug(f"🔵🔵🔵 Running edit_playlist for {playlist.name}")
        set_editing(True)

    def time_since_update(playlist):
        t = datetime.now() - playlist.last_update_completed

        if t.seconds > (24 * 3600):
            return str(f"{t.days} days ago")
        elif t.seconds > 3600:
            return str(f"{t.seconds // 3600} hours ago")
        elif t.seconds < 3600 and t.seconds > 60:
            return str(f"{(t.seconds // 60)} minutes ago")
        else:
            return str(f"Just now")

    since_updated, set_since_updated = solara.use_state(time_since_update(playlist))
    editing, set_editing = solara.use_state(False)

    if editing:
        logger.debug(f"🟣🟣🟣 Editing = {editing}, Playlist = {playlist.name}")
        edit_button_text = "Cancel"
    else:
        edit_button_text = "Edit Playlist"

    if updated:
        logger.debug(
            f"🟢🟢🟢 Updated = {updated}, Since updated = {since_updated}, Playlist = {playlist.name}"
        )
        set_since_updated(time_since_update(playlist))
        set_updated(False)

    elif loading:
        with solara.Card(classes=["playlist-card"]):
            solara.SpinnerSolara(size="100px")
            solara.Markdown(f"## {playlist.name}")
            solara.Markdown("Loading...")
    else:

        with solara.Card(classes=["playlist-card"]):
            if editing:
                solara.Markdown(f"## {playlist.name}")
                # solara.Markdown(f"#### {len(playlist.videos)} videos")
                solara.Markdown(f"#### YT Channel: Harry Mack Clips")
                solara.Markdown(f"#### 87 Videos Found 60 downloaded")
                edit_func = lambda: edit_playlist(playlist)
                update_func = lambda: update_playlist_videos(playlist)
                # refresh_func = lambda: set_since_updated(time_since_update(playlist))

                logger.debug(f"Since updated={since_updated}")

                with solara.Column(
                    align="center", classes=["playlist-card-button_section"]
                ):
                    solara.Button(
                        edit_button_text,
                        on_click=lambda: set_editing(not editing),
                        classes=["mybutton, playlist-card-button"],
                    )

                    solara.Button(
                        "Update playlist",
                        on_click=update_func,
                        classes=["mybutton, playlist-card-button"],
                    )
                    # solara.Button(
                    #     "Refresh Updated Time", on_click=refresh_func, classes=["mybutton"]
                    # )
                with solara.Column(align="end", classes=["playlist-card-footer"]):

                    solara.Text(
                        f"Be careful. In Editing Mode",
                    )
            else:
                solara.Markdown(f"## {playlist.name}")
                # solara.Markdown(f"#### {len(playlist.videos)} videos")
                solara.Markdown(f"#### YT Channel: Harry Mack Clips")
                solara.Markdown(f"#### 87 Videos Found 60 downloaded")
                edit_func = lambda: edit_playlist(playlist)
                update_func = lambda: update_playlist_videos(playlist)
                # refresh_func = lambda: set_since_updated(time_since_update(playlist))

                logger.debug(f"Since updated={since_updated}")

                with solara.Column(
                    align="center", classes=["playlist-card-button_section"]
                ):
                    solara.Button(
                        edit_button_text,
                        on_click=lambda: set_editing(not editing),
                        classes=["mybutton, playlist-card-button"],
                    )

                    solara.Button(
                        "Update playlist",
                        on_click=update_func,
                        classes=["mybutton, playlist-card-button"],
                    )
                    # solara.Button(
                    #     "Refresh Updated Time", on_click=refresh_func, classes=["mybutton"]
                    # )
                with solara.Column(align="end", classes=["playlist-card-footer"]):

                    solara.Text(
                        f"Last updated: {since_updated}",
                    )


@solara.component
def PlaylistsBySeriesGroup(series):
    playlists, set_playlists = solara.use_state(None)
    # playlist, set_playlist = solara.use_state(None)
    updated, set_updated = solara.use_state(False)
    loading, set_loading = solara.use_state(True)

    if loading and playlists is None:
        logger.debug("🙁🙁🙁 loading and playlists == []")
        set_playlists(get_playlists(series))
        logger.debug(f"🔵🔵🔵 Playlists = {playlists}")
        with solara.Column(classes=["playlist-group"]):
            solara.Markdown(
                f"# Loading...",
            )
        set_loading(False)

    elif playlists and not loading:
        logger.debug("🐣🐣🐣 playlists and not loading")

        # solara.Markdown(f"#### {len(playlist.videos)} videos")
        with solara.Column(classes=["playlist-group"]):
            solara.Markdown(
                f"# {playlists[0].series.name}",
            )
            with solara.ColumnsResponsive(12, large=[6, 6]):

                cards = []
                for playlist in playlists:

                    # with solara.Row(style={"border": "10px solid #fff0ff"}):

                    # set_since_updated(time_since_update())
                    cards.append(playlist)
                    PlaylistCard(
                        playlist,
                        loading,
                        set_loading,
                        updated,
                        set_updated,
                    )
                # if len(cards) > 0 and len(cards) < 4:
                #     with solara.Card(classes=["playlist-card"]):
                #         with solara.Column(
                #             align="center", classes=["playlist-card-button_section"]
                #         ):
                #             solara.Button(
                #                 "Add New Playlist",
                #                 on_click=lambda: logger.debug("Add playlist"),
                #                 classes=["mybutton", "playlist-card-button"],
                #             )

    else:
        logger.debug(
            f"🟡🟡🟡 in the else clause playlists exists and loading =  {loading}"
        )
        with solara.Column(classes=["playlist-group"]):

            solara.Markdown(
                f"# {series.name} blahblah",
            )
            with solara.Card(classes=["playlist-card", "playlist-card-button_section"]):
                solara.Button(
                    "Add New Playlist",
                    on_click=lambda: logger.debug("Add playlist"),
                    classes=["mybutton", "playlist-card-button"],
                )


@solara.component
def Page():

    MyAppBar()

    for series in get_series():
        PlaylistsBySeriesGroup(series)
