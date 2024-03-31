from flask import Flask
from flask_admin import Admin
from flask_peewee.db import Database

from hmtc.config import init_config
from hmtc.utils.my_logging import setup_logging
from hmtc.utils.general import clear_screen
from hmtc.db import setup_db, import_existing_tracks, import_existing_video_files_to_db
from hmtc.admin_views import (
    UserAdmin,
    PostAdmin,
    PlaylistAdmin,
    SeriesAdmin,
    VideoAdmin,
)
from loguru import logger
from pathlib import Path
from datetime import timedelta, datetime
import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table, page_container
import plotly.express as px
import pandas as pd

import dash_bootstrap_components as dbc

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def setup_dash_app(flask_app):
    app = Dash(
        __name__, use_pages=True, external_stylesheets=[dbc.themes.QUARTZ, dbc_css]
    )

    app.layout = dbc.Container(
        [
            dbc.Row(dbc.Col(html.H1("HMTC"))),
            dbc.Row(
                [
                    dbc.Col(
                        html.H3(dcc.Link(f"{page['name']}", href=page["relative_path"]))
                    )
                    for page in dash.page_registry.values()
                ]
            ),
            dash.page_container,
        ],
        className="dbc",
    )

    return app


def setup_app(db):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "86753098675309"
    return app


def setup_admin(app):
    admin = Admin(app, name="HMTC")
    admin.add_view(UserAdmin.view())
    admin.add_view(PostAdmin.view())
    admin.add_view(PlaylistAdmin.view())
    admin.add_view(VideoAdmin.view())
    admin.add_view(SeriesAdmin.view())
