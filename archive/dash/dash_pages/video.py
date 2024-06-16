import dash
import dash_bootstrap_components as dbc
import dash_player
from dash import html

from hmtc.models import File, Section, Video

dash.register_page(__name__, path_template="/video/<video_id>")


# card_header = dbc.CardHeader("Controls")

# card_body = dbc.CardBody(
#     [
#         dbc.Row(
#             html.Div(
#                 [
#                     dbc.Col(
#                         html.H3(
#                             "Controls",
#                             id="example-output",
#                             style={
#                                 "verticalAlign": "middle",
#                                 "fontWeight": "bold",
#                                 "textAlign": "center",
#                             },
#                         )
#                     ),
#                 ]
#             ),
#             # style={"className": "row row-cols-2 row-cols-lg-5 g-2 g-lg-3"},
#         ),


#                 ]
#             ),
#         ),
#         # style={"className": "row row-cols-2 row-cols-lg-5 g-2 g-lg-3"},
#         dbc.Row(
#             html.Div(
#                 [
#                     dbc.Button("Reset", id="reset", className="me-md-2"),
#                     dbc.Button("Play Snippet", id="snippet", className="me-md-2"),
#                     dbc.Button("Pause", id="pause", className="button-29"),
#                 ],
#                 className="d-grid gap-2 d-md-flex justify-content-md-center",
#             ),
#             # style={"className": "row row-cols-2 row-cols-lg-5 g-2 g-lg-3"},
#         ),
#     ]
# )

buttons = [
    html.Button(
        "--",
        id="coarse_rewind",
        className="button-29",
    ),
    html.Button("-", id="fine_rewind", className="button-29"),
    html.Button("Timer", id="current_time_display", className="button-29"),
    html.Button("+", id="fine_forward", className="button-29"),
    html.Button("++", id="coarse_forward", className="button-29"),
]


# video.files[0].local_path should work in prod
def video_path(filename, extension):
    return "assets/" + filename + extension


home_row_card = dbc.Card(dbc.CardBody(html.H1("Home Row", id="home_row")))


def section_cards(sections):
    return html.Div(
        [
            html.H1(
                f"{section.start}s - {section.end}s)",
                className="section_card",
            )
            for section in sections
            if section.section_type == "music"
        ],
    )


def video_player(file):
    return dash_player.DashPlayer(
        id="player",
        url=video_path(file.filename, file.extension),
        controls=True,
        width="400px",
    )


def layout(video_id=None):
    if video_id is None or video_id == "None":
        return html.Div("No video selected")
    video = (
        Video.select(
            Video.title,
            Video.id,
            File.filename,
            File.extension,
            File.local_path,
            Section.start,
            Section.end,
            Section.section_type,
        )
        .join(Section)
        .switch(Video)
        .join(File)
        .where(Video.id == video_id)
        .get()
    )

    return html.Div(
        [
            html.Div(html.H5(video.title)),
            html.Div(
                video_player(video.files[0]),
                className="my_card",
                style={"min-width": "450px"},
            ),
            html.Div(buttons, className="my_card"),
            html.Div(home_row_card, className="my_card"),
            html.Div(section_cards(video.sections), className="my_card"),
            html.Div(
                [
                    f"({file.local_path}/{file.filename}{file.extension})"
                    for file in video.files
                ],
                className="my_card",
            ),
        ]
    )


# @callback(
#     Output("current_time_display", "children"),
#     Input("video_player", "currentTime"),
# )
# def update_timer_label(currentTime):
#     if not currentTime:
#         return "000.000"
#     return f"{currentTime:.3f}"


# @callback(
#     Output("output", "children"),
#     Output("home_row", "children"),
#     Input("radios", "value"),
# )
# def display_value(value):
#     section = Section.get_by_id(value)

#     return f"Selected value: {value}", section.start


# @callback(
#     Output("player", "seekTo"),
#     Input("coarse_rewind", "n_clicks"),
#     State("player", "currentTime"),
# )
# def coarse_rewind(n_clicks, currentTime):
#     REWIND_TIME = 5
#     if n_clicks is None:
#         return None
#     if currentTime > REWIND_TIME:
#         return currentTime - REWIND_TIME


# @callback(
#     Output("player", "seekTo"),
#     Input("fine_rewind", "n_clicks"),
#     State("player", "currentTime"),
# )
# def fine_rewind(n_clicks, currentTime):
#     REWIND_TIME = 1
#     if n_clicks is None:
#         return None
#     if currentTime > REWIND_TIME:
#         return currentTime - REWIND_TIME


# @callback(
#     Output("player", "seekTo"),
#     Output("player", "playing"),
#     Input("coarse_forward", "n_clicks"),
#     State("player", "currentTime"),
# )
# def update_video_state(n_clicks, currentTime):
#     if n_clicks is None:
#         return None, None

#     return currentTime + 5, False


# @callback(
#     Output("player", "playing"),
#     Input("snippet", "n_clicks"),
#     State("player", "playing"),
# )
# def explay_snippet(n_clicks, is_playing):
#     if n_clicks is None:
#         return False
#     return not is_playing


# @callback(
#     Output("player", "seekTo"),
#     Input("coarse_rewind", "n_clicks"),
#     Input("fine_rewind", "n_clicks"),
#     Input("fine_forward", "n_clicks"),
#     Input("coarse_forward", "n_clicks"),
#     State("player", "currentTime"),
# )
# def display(btn1, btn2, btn3, btn4, currentTime):
#     button_id = ctx.triggered_id if not None else "No clicks yet"
#     if currentTime is None:
#         currentTime = 0
#     match button_id:
#         case "coarse_rewind":
#             return currentTime - 5
#         case "fine_rewind":
#             return currentTime - 1
#         case "fine_forward":
#             return currentTime + 1
#         case "coarse_forward":
#             return currentTime + 5
#         case _:
#             return 0

#     ctx_msg = json.dumps(
#         {"states": ctx.states, "triggered": ctx.triggered, "inputs": ctx.inputs},
#         indent=2,
#     )


# @callback(
#     Output("player", "playing"),
#     Output("player", "loop"),
#     Output("player", "controls"),
#     Output("player", "muted"),
#     Input("bool-props-radio", "value"),
# )
# def update_bool_props(values):
#     playing = "playing" in values
#     loop = "loop" in values
#     controls = "controls" in values
#     muted = "muted" in values
#     return playing, loop, controls, muted


# @callback(
#     Output("player", "seekTo"),
#     Input("forward-fine-btn", "n_clicks"),
#     State("player", "currentTime"),
# )
# def on_button_click(n, currentTime):
#     if n is None:
#         return 0
#     else:
#         if currentTime is None:
#             currentTime = 0
#         return int(currentTime) + 1.0


# @callback(
#     Output("current-time-div", "children"),
#     Input("player", "currentTime"),
# )
# def display_currentTime(currentTime):
#     return f"Current Time: {currentTime}"


# @callback(
#     Output("seconds-loaded-div", "children"),
#     Input("player", "secondsLoaded"),
# )
# def display_secondsLoaded(secondsLoaded):
#     return f"Second Loaded: {secondsLoaded}"


# @callback(
#     Output("duration-div", "children"),
#     Input("player", "duration"),
# )
# def display_duration(duration):
#     return f"Duration: {duration}"


# @callback(
#     Output("player", "volume"),
#     Input("volume-slider", "value"),
# )
# def set_volume(value):
#     return value


# @callback(
#     Output("player", "playbackRate"),
#     Input("playback-rate-slider", "value"),
# )
# def set_playbackRate(value):
#     return value


# @callback(
#     Output("player", "intervalCurrentTime"),
#     Input("intervalCurrentTime-slider", "value"),
# )
# def set_intervalCurrentTime(value):
#     return value


# @callback(
#     Output("player", "intervalSecondsLoaded"),
#     Input("intervalSecondsLoaded-slider", "value"),
# )
# def set_intervalSecondsLoaded(value):
#     return value


# @callback(
#     Output("player", "intervalDuration"),
#     Input("intervalDuration-slider", "value"),
# )
# def set_intervalDuration(value):
#     return value


# this stuff was previoulsy commented out


# @callback(
#     Output("player", "seekTo"),
#     Input("seekto-number-btn", "n_clicks"),
#     State("seekto-number-input", "value"),
# )
# def set_prop_seekTo(n_clicks, seekto):
#     return seekto

# @callback(
#     Output("example-output_lbl", "children"),
#     # Input("player", "currentTime"),
#     Input("forward-fine-btn", "n_clicks"),
# )
# def set_prop_seekTo(n_clicks, currentTime, children):
#     if currentTime is not None:
#         children = currentTime + 1
#         return children
#     return "0"


# video_sliders = dbc.Row(
#     style={"width": "48%", "padding": "10px"},
#     children=[
#         html.P("Volume:", style={"marginTop": "30px"}),
#         dcc.Slider(
#             id="volume-slider",
#             min=0,
#             max=1,
#             step=0.05,
#             value=0.5,
#             updatemode="drag",
#             marks={0: "0%", 0.5: "50%", 1: "100%"},
#         ),
#         html.P("Playback Rate:", style={"marginTop": "25px"}),
#         dcc.Slider(
#             id="playback-rate-slider",
#             min=0,
#             max=2,
#             step=None,
#             updatemode="drag",
#             marks={i: str(i) + "x" for i in [0, 0.5, 1, 1.5, 2]},
#             value=1,
#         ),
#         html.P(
#             "Update Interval for Current Time:",
#             style={"marginTop": "30px"},
#         ),
#         dcc.Slider(
#             id="intervalCurrentTime-slider",
#             min=0,
#             max=1000,
#             step=None,
#             updatemode="drag",
#             marks={i: str(i) for i in [0, 250, 500, 750, 1000]},
#             value=250,
#         ),
#         html.P(
#             "Update Interval for Seconds Loaded:",
#             style={"marginTop": "30px"},
#         ),
#         dcc.Slider(
#             id="intervalSecondsLoaded-slider",
#             min=0,
#             max=1000,
#             step=None,
#             updatemode="drag",
#             marks={i: str(i) for i in [0, 250, 500, 750, 1000]},
#             value=500,
#         ),
#         html.P(
#             "Update Interval for Duration:",
#             style={"marginTop": "30px"},
#         ),
#         dcc.Slider(
#             id="intervalDuration-slider",
#             min=0,
#             max=1000,
#             step=None,
#             updatemode="drag",
#             marks={i: str(i) for i in [0, 250, 500, 750, 1000]},
#             value=500,
#         ),
#     ],
# )
