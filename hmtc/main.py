from hmtc.config import init_config
from hmtc.utils.my_logging import setup_logging
from hmtc.utils.general import clear_screen
from hmtc.db import setup_db, import_existing_tracks, import_existing_video_files_to_db
from loguru import logger
from pathlib import Path
from datetime import timedelta, datetime
import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table, page_container
import plotly.express as px
import pandas as pd
from hmtc.app import setup_app, setup_dash_app, setup_admin
import dash_bootstrap_components as dbc

# from hmtc.section_manager import SectionManager

from hmtc.models import Playlist, Series, Video, Section, get_section_with_timestamp


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def update_playlists():
    playlists = Playlist().select().join(Series).where(Playlist.enabled == True)

    for p in playlists:
        now = datetime.now()
        last_completed = p.last_update_completed
        if not last_completed or (now - last_completed > timedelta(hours=1)):
            p.check_for_new_videos()


def create_video_sections():
    for vid in Video.select():
        vid.create_initial_section()


def main():
    clear_screen()

    config = init_config()
    setup_logging(config)

    db = setup_db(config)

    app = setup_app(db)
    dash_app = setup_dash_app(app)
    admin = setup_admin(app)
    dash_app.run(debug=True)
    # dash_app.run(debug=True)
    exit()
    # this is the end of the main app loop.
    # code below is only temporary...
    # move it above the app.run command to have it execute

    # needs to be run on a schedule
    update_playlists()

    # using for testing

    # can be removed once everything is setup
    create_video_sections()
    track_csv = config.get("IMPORT", "TRACK_INFO")
    import_existing_tracks(track_csv)

    video_path = config.get("MEDIA", "VIDEO_PATH")
    import_existing_video_files_to_db(video_path)

    # actually start the app loop

    # app = HMTCApp()
    # app.run()

    db.close()


if __name__ == "__main__":
    main()
