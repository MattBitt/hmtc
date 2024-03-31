from dash import Dash, dcc, html, Input, Output
import random
import plotly.express as px
import pandas as pd

df = pd.DataFrame.from_dict([{"x": val, "y": random.random()} for val in range(10)])


app = Dash(__name__)


app.layout = html.Div(
    [
        dcc.Graph(figure=px.bar(df, x="x", y="y")),
        html.Div(
            [html.Div(html.H1(n), className="cardBorders") for n in range(10)],
            className="grid alignCards",
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
