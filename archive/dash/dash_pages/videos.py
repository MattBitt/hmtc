import dash
import dash_bootstrap_components as dbc
from dash import dash_table, html

from hmtc.models import VideoModel

dash.register_page(__name__)

COLUMNS = ["youtube_id", "title", "upload_date"]

table_data = [d for d in VideoModel.select().dicts()]
table = html.Div(
    dash_table.DataTable(
        table_data,
        columns=[{"name": i, "id": i} for i in COLUMNS],
        id="table",
        page_size=20,
        row_selectable="multi",
        sort_action="native",
        filter_action="native",
        style_header={
            "backgroundColor": "rgb(30, 30, 30)",
            "color": "white",
            "font-weight": "bold",
        },
        style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
    )
)

video_table = dbc.Container(table)

layout = html.Div(
    [
        html.Div(video_table, id="videos-table"),
    ]
)
