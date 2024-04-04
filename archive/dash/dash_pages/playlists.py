import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc
from hmtc.models import Playlist, Series
from playhouse.shortcuts import model_to_dict
import pandas as pd
from dash import Input, Output, callback

dash.register_page(__name__)


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def prep_data(data):
    s = data.series.name
    # remove object from dict
    new_data = model_to_dict(data)
    new_data["series"] = s
    return new_data


query = Playlist.select(Playlist, Series).join(Series).switch(Playlist)
playlists = [prep_data(result) for result in query]
COLUMNS = ["name", "url", "last_update_completed", "series"]

table = html.Div()


layout = html.Div(
    [
        html.H1("Playlists"),
        html.Br(),
        dbc.Container(
            dash_table.DataTable(
                playlists,
                columns=[{"name": i, "id": i} for i in COLUMNS],
                page_size=20,
                id="playlists-table",
                row_selectable="multi",
                sort_action="native",
                filter_action="native",
            ),
            className="dbc",
        ),
        dbc.Container(dbc.Alert(), id="status_bar", className="dbc"),
        # html.Div(playlists_table, id="playlists-table"),
    ]
)


@callback(Output("status_bar", "children"), Input("playlists-table", "active_cell"))
def update_graphs(active_cell):
    return str(active_cell) if active_cell else "Click the table"
