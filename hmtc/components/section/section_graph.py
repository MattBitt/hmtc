import pandas as pd
from hmtc.assets.colors import Colors
import plotly.express as px
import plotly.graph_objects as go
import solara
from loguru import logger


def to_dt(ts):
    return pd.to_datetime(ts, unit="s")


def format_sections(sections, width=1800):
    # takes a list of sections from a Video and formats them for the timeline graph

    def format_string(ts):
        return f"{str(ts // 60).zfill(2)}:{str(ts % 60).zfill(2)} ({ts})"

    graph_sections = []
    for sect in sections:
        abs_start = sect.start
        abs_end = sect.end
        section_id = sect.id
        start_row = abs_start // width
        end_row = abs_end // width
        start_string = f"{str(abs_start // 60).zfill(2)}:{str(abs_start % 60).zfill(2)} ({abs_start})"
        end_string = (
            f"{str(abs_end // 60).zfill(2)}:{str(abs_end % 60).zfill(2)} ({abs_end})"
        )

        if start_row == end_row:
            section = dict()
            section["id"] = section_id
            section["start_ts"] = to_dt(abs_start - (width * start_row))
            section["end_ts"] = to_dt(abs_end - (width * end_row))
            section["hour"] = -start_row
            section["duration"] = abs_end - abs_start
            section["start_string"] = start_string
            section["end_string"] = end_string
            section["type"] = sect.section_type
            graph_sections.append(section)
        else:
            # logger.debug(
            #     f"Start row and End Row are not equal for id {section_id} {start_row},{end_row}"
            # )
            section1 = dict(
                start=abs_start,
                end=width,
                id=section_id,
                hour=-start_row,
            )
            section1["start_ts"] = to_dt(abs_start - (width * start_row))
            section1["end_ts"] = to_dt(width)
            section1["hour"] = -start_row
            section1["id"] = section_id

            section2 = dict(
                start=0,
                end=abs_end - (width * end_row),
                id=section_id,
                hour=-end_row,
                type=sect.section_type,
            )
            section2["start_ts"] = to_dt(0)
            section2["end_ts"] = to_dt(abs_end - (width * end_row))
            section2["hour"] = -end_row
            section2["duration"] = section2["end"]
            section2["id"] = section_id
            # logger.debug(f"New Section1 {section1}")
            # logger.debug(f"New Section2 {section2}")

            section1["start_string"] = start_string
            section1["end_string"] = end_string
            section2["start_string"] = start_string
            section2["end_string"] = end_string
            section1["duration"] = abs_end - abs_start
            section2["duration"] = section1["duration"]
            graph_sections.append(section1)
            graph_sections.append(section2)

    return graph_sections


@solara.component
def SectionGraphComponent(
    sections, current_selection, on_click, max_section_width=1800, max_section_height=24
):
    def handle_hover(*args):
        # logger.error(f"Graph Component Hovered Over")
        # logger.debug(f"args: {args}")
        pass

    def handle_click(*args):
        logger.error(f"Graph Component Clicked args={args}")
        pindex = args[0]["points"]["point_indexes"][0]
        logger.debug(f"Point Index: {pindex}")
        on_click(formatted_sections[pindex])

    # logger.error(f"Current Selection: {current_selection.value}")

    formatted_sections = format_sections(sections, width=max_section_width)
    if len(formatted_sections) == 0:
        logger.debug("No formatted sections to display")
        return solara.Markdown("No Sections to Display")

    fig = px.timeline(
        formatted_sections,
        x_start="start_ts",
        x_end="end_ts",
        y="hour",
        color="type",
        color_discrete_map={
            "instrumental": str(Colors.PRIMARY),
        },
        range_x=[to_dt(0), to_dt(max_section_width)],
        range_y=[-max_section_height - 0.5, 0.5],
        hover_name="id",
        hover_data={
            "start_string": True,
            "end_string": True,
            "id": False,
            "hour": False,
            "duration": True,
            "start_ts": False,
            "end_ts": False,
        },
    )

    fig.update_layout(
        plot_bgcolor=str(Colors.SURFACE),
        xaxis={"tickformat": "%H:%M"},
        yaxis={"dtick": 1},
        showlegend=False,
        # annotations=list(fig.layout.annotations)
        # + [
        #     go.layout.Annotation(
        #         x=0.5,
        #         y=-0.2,
        #         font=dict(size=16, color=str(Colors.PRIMARY)),
        #         showarrow=False,
        #         text="time",
        #         textangle=-0,
        #         xref="paper",
        #         yref="paper",
        #     )
        # ],
    )
    solara.FigurePlotly(fig, on_click=handle_click, on_hover=handle_hover)
