import datetime
import time

import pandas as pd
import plotly.express as px
import solara
from loguru import logger

from hmtc.assets.colors import Colors


def seconds_to_pd_datetime(ts):
    pd_dt = pd.to_datetime(ts, unit="ms")
    time_string = pd_dt.strftime("%Y-%m-%d %H:%M:%S")
    return time_string


def format_string(ts):
    return f"{str(ts // 3600_000).zfill(2)}:{str(ts // 60_000).zfill(2)}:{str(ts % 60_000).zfill(2)} ({ts})"


def format_sections(sections, selected_index, width=1800000):
    # width = 1800000 corresponds to 30 minutes
    # for now, that will be the limit

    graph_sections = []
    for sect in sections:
        graph_sections.append(
            dict(
                id=sect.id,
                start_ts=seconds_to_pd_datetime(sect.start),
                end_ts=seconds_to_pd_datetime(sect.end),
                # used as row, actually half an hour (1800)
                hour=(sect.end - sect.start) // width,
                duration=sect.end - sect.start,
                start_string=format_string(sect.start),
                end_string=format_string(sect.end),
                type=sect.section_type,
                selected=False,
            )
        )
    graph_sections[selected_index]["selected"] = True
    return graph_sections


@solara.component
def SectionGraphComponent(
    formatted_sections,
    on_click,
    max_section_width=1800,
    max_section_height=24,
):
    def handle_hover(*args):
        # logger.error(f"Graph Component Hovered Over")
        # logger.debug(f"args: {args}")
        pass

    def handle_click(*args):
        # logger.error(f"Graph Component Clicked args={args}")
        try:
            # return the 'end' time in seconds. won't work for
            # multirow sections
            on_click(args[0]["points"]["point_indexes"][0])
            return
            time_string = args[0]["points"]["xs"][0]
            if len(time_string) == 16:
                # not sure why i need this
                time_string = time_string + ":00"

            x = time.strptime(time_string, "%Y-%m-%d %H:%M:%S")
            seconds = datetime.timedelta(
                hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
            ).total_seconds()
            on_click(int(seconds))
        except Exception as e:
            logger.error(f"Exception {e}")
            return

    fig = px.timeline(
        formatted_sections,
        x_start="start_ts",
        x_end="end_ts",
        y="hour",
        color="type",
        color_discrete_map={
            "instrumental": str(Colors.PRIMARY),
        },
        pattern_shape="selected",
        pattern_shape_map={True: "/", False: ""},
        range_x=[
            seconds_to_pd_datetime(0),
            seconds_to_pd_datetime(max_section_width),
        ],
        range_y=[-max_section_height - 0.5, 0.5],
        hover_name="id",
        hover_data={
            "start_string": True,
            "end_string": True,
            "id": False,
            "hour": True,
            "duration": True,
            "start_ts": False,
            "end_ts": False,
            "selected": True,
        },
    )

    fig.update_layout(
        plot_bgcolor=str(Colors.SURFACE),
        xaxis={"tickformat": "%H:%M:%S", "autorange": True},
        yaxis={"showticklabels": False, "autorange": True},
        showlegend=False,
    )
    solara.FigurePlotly(fig, on_click=handle_click, on_hover=handle_hover)
