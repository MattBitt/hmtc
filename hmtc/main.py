from hmtc.config import init_config
from hmtc.utils.my_logging import setup_logging
from hmtc.db import setup_db, import_existing_tracks, import_existing_video_files_to_db

import pandas as pd
from hmtc.app import setup_app, setup_admin


# from hmtc.section_manager import SectionManager



df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def setup():
    config = init_config()
    setup_logging(config)
    db = setup_db(config)
    return db, config


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
    main2()
