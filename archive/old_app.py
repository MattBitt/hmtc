import dash
import dash_bootstrap_components as dbc
import pandas as pd
import solara.server.flask
from dash import Dash, html
from flask import Flask
from flask_admin import Admin

from hmtc.admin_views import (PlaylistAdmin, PostAdmin, SeriesAdmin, UserAdmin,
                              VideoAdmin)

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

# I think this is for DataTables. I'm not sure if it's necessary.
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def setup_dash_app(flask_app):
    app = Dash(
        __name__,
        use_pages=True,
        external_stylesheets=[dbc.themes.QUARTZ, dbc_css, dbc.icons.BOOTSTRAP],
        url_base_pathname="/",
        server=flask_app,
    )

    page_header = dbc.Row(dbc.Col())
    # nav_bar = html.Nav(
    #     [
    #         html.H3(
    #             dcc.Link(
    #                 f"{page['name']}", href=page["relative_path"], className="nav-link"
    #             )
    #         )
    #         for page in dash.page_registry.values()
    #     ]
    # )

    def nav_item(page):
        return dbc.NavLink(
            f"{page['name']}",
            href=page["relative_path"],
            # class_name="nav-link",
            active=True,
        )

    brand = html.Div(
        [
            html.Span(html.I(className="bi bi-boombox-fill brand")),
            html.Span("HMTC", className="brand"),
        ]
    )
    navbar = dbc.NavbarBrand(
        children=[
            dbc.NavLink(brand, href="#"),
            html.Div([nav_item(page) for page in dash.page_registry.values()]),
        ],
    )

    app.layout = html.Div(
        [
            navbar,
            dash.page_container,
        ],
        className="dbc",
        id="container",
    )

    return app


def setup_app(db):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "86753098675309"
    app.register_blueprint(solara.server.flask.blueprint, url_prefix="/solara/")
    return app


def setup_admin(app):
    admin = Admin(app, name="HMTC")
    admin.add_view(UserAdmin.view())
    admin.add_view(PostAdmin.view())
    admin.add_view(PlaylistAdmin.view())
    admin.add_view(VideoAdmin.view())
    admin.add_view(SeriesAdmin.view())
