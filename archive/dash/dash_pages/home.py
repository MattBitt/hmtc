import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")


def card(id):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(f"Card #{id}", className="card-title"),
                    html.P(
                        "Some quick example text to build on the card title and "
                        "make up the bulk of the card's content.",
                        className="card-text",
                    ),
                    dbc.Button("Go somewhere", color="primary"),
                ]
            ),
        ],
        class_name="card" + str(id) + " col",
    )


layout = html.Div(
    [
        html.H1("This is our Home page"),
        html.Div("This is our Home page content."),
        html.Div([card(1), card(2), card(3)], className="container"),
        dbc.CardGroup(
            [card(4), card(5), card(6)],
        ),
    ]
)
