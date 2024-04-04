import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc
from hmtc.models import Series

dash.register_page(__name__)
COLUMNS = ["name", "start_date", "end_date"]

table_data = [d for d in Series.select().dicts()]
table = html.Div(
    dash_table.DataTable(
        table_data,
        columns=[{"name": i, "id": i} for i in COLUMNS],
        id="table",
        page_size=20,
        style_as_list_view=False,
    )
)

series_table = dbc.Container(table, className="dbc dbc-row-selectable")

layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                html.H3(
                                    children=series["name"],
                                    className="text-center text-light bg-dark",
                                ),
                                body=True,
                                color="dark",
                            ),
                            className="mb-4",
                        )
                    ]
                )
                for series in table_data
            ]
        ),
        html.Br(),
        dbc.Container(dbc.Alert(), id="status_bar", className="dbc"),
    ]
)
