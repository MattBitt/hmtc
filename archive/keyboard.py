import json

from dash_extensions.enrich import DashProxy, html, Input, Output, State, dcc
from dash_extensions import Keyboard

# Create small example app
app = DashProxy()
app.layout = html.Div(
    [
        Keyboard(
            captureKeys=["Enter", "a", "b", "c"],
            id="keyboard",
        ),
        html.Div(id="log"),
    ]
)


@app.callback(
    Output("log", "children"),
    Input("keyboard", "n_keydowns"),
    State("keyboard", "keydown"),
)
def track_keydown(_, event):
    return json.dumps(event)


if __name__ == "__main__":
    app.run_server()
