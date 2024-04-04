from hmtc.config import init_config
from hmtc.utils.my_logging import setup_logging
from hmtc.db import setup_db, import_existing_tracks, import_existing_video_files_to_db
from datetime import timedelta, datetime
import pandas as pd
from hmtc.app import setup_app, setup_dash_app, setup_admin

from loguru import logger

# from hmtc.section_manager import SectionManager

from hmtc.models import Playlist, Series, Video


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def update_playlist(playlist):
    now = datetime.now()
    logger.info(f"Checking playlist {playlist.name}")
    last_completed = playlist.last_update_completed
    if not last_completed or (now - last_completed > timedelta(seconds=20)):
        playlist.check_for_new_videos()


def update_playlists():
    logger.warning("Updating playlists")
    playlists = Playlist().select().join(Series).where(Playlist.enabled == True)

    for p in playlists:
        update_playlist(p)


def create_video_sections():
    for vid in Video.select():
        vid.create_initial_section()


def setup():
    config = init_config()
    setup_logging(config)
    db = setup_db(config)
    return db


def main2():
    # clear_screen()

    config = init_config()
    setup_logging(config)

    db = setup_db(config)

    app = setup_app(db)
    # update_playlists()
    setup_admin(app)
    app.run(debug=False)
    # dash_app = setup_dash_app(app)
    # dash_app.run_server(debug=True)
    db.close()
    # dash_app.run(debug=True)
    exit()
    # this is the end of the main app loop.
    # code below is only temporary...
    # move it above the app.run command to have it execute

    # needs to be run on a schedule

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


if __name__ == "__main__":
    main()
