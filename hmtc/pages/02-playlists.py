import solara
import solara.lab
from archive.sol import sidebar, main_content
from hmtc.components.app_bar import AppBar
from hmtc.models import Playlist, Video, Series
from hmtc.main import update_playlist
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger


def get_playlists(series=None):
    query = Playlist.select().join(Series).order_by(Series).order_by(Playlist.name)
    if series:
        query = query.where(Playlist.series == series)
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
        solara.Button("Add playlist", on_click=lambda: logger.debug("Add playlist"))


@solara.component
def PlaylistCard(playlist, loading, since_updated, update_func):
    logger.info(f"Inside Playlist card playlist id = {playlist.id}")

    if loading:
        with solara.Card():
            solara.Markdown(f"## {playlist.name}")
            solara.Markdown("Loading...")
    else:
        with solara.Card():
            solara.Markdown(f"## {playlist.name}")

            logger.info(f"Since updated={since_updated}")

            edit_func = lambda: logger.debug("Edit playlist")
            # set_since_updated(datetime.now() - playlist.last_update_completed)
            solara.Markdown(f"Last updated: {since_updated}")

            solara.Button(
                "Edit Playlist",
                on_click=edit_func,
            )

            solara.Button(
                "Update playlist",
                on_click=update_func,
            )
            # solara.Button(
            #     "Refresh",
            #     on_click=refresh_func(),
            # )


@solara.component
def SeriesGroup(series):
    playlists, set_playlists = solara.use_state(None)
    since_updated, set_since_updated = solara.use_state("----")
    loading, set_loading = solara.use_state(True)

    def time_since_update():
        t = datetime.now() - playlist.last_update_completed
        return str(f"{(t.seconds // 60)} minutes ago")

    def update_playlist_videos():
        logger.error("💥💥💥 Running update_playlist_videos")
        set_loading(True)
        playlist.check_for_new_videos()
        set_since_updated(time_since_update())
        set_loading(False)

    if loading and not playlists:
        set_playlists(get_playlists(series))
        set_loading(False)

    if playlists:
        # if a series has playlists display the card
        with solara.Column():

            solara.Markdown(
                f"# {playlists[0].series.name}",
                style={"border": "10px solid #0000ff"},
            )

            with solara.Row(style={"border": "1px solid #0000ff"}):
                for playlist in playlists:

                    PlaylistCard(
                        playlist,
                        loading,
                        since_updated,
                        update_playlist_videos,
                    )


@solara.component
def Page():

    AppBar()

    for series in get_series():
        SeriesGroup(series)

    with solara.Row():
        PlaylistButton()
