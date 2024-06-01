import solara
import pandas as pd
import plotly.express as px
from loguru import logger


@solara.component
def SectionGraphComponent(
    sections, current_selection, on_click, max_section_width=1800
):

    def handle_hover(*args, **kwargs):
        # logger.error(f"Graph Component Hovered Over")
        # logger.debug(f"args: {args}")
        # logger.debug(f"kwargs: {kwargs}")
        pass

    def to_dt(ts):
        return pd.to_datetime(ts, unit="s")

    def format_sections():

        graph_sections = []
        for sect in sections:
            abs_start = sect.start
            abs_end = sect.end
            section_id = sect.id
            start_row = abs_start // max_section_width
            end_row = abs_end // max_section_width
            start_string = f"{str(abs_start // 60).zfill(2)}:{str(abs_start % 60).zfill(2)} ({abs_start})"
            end_string = f"{str(abs_end // 60).zfill(2)}:{str(abs_end % 60).zfill(2)} ({abs_end})"
            logger.debug(
                f"Calulated start and end rows for ID: {section_id} {start_row},{end_row}"
            )
            if start_row == end_row:
                logger.debug(
                    f"Start row and End Row are equal ID: {section_id} {start_row},{end_row}"
                )
                section = dict()
                section["id"] = section_id
                section["start_ts"] = to_dt(abs_start - (max_section_width * start_row))
                section["end_ts"] = to_dt(abs_end - (max_section_width * end_row))
                section["hour"] = -start_row
                section["duration"] = abs_end - abs_start
                section["start_string"] = start_string
                section["end_string"] = end_string
                graph_sections.append(section)
            else:
                logger.debug(
                    f"Start row and End Row are not equal for id {section_id} {start_row},{end_row}"
                )
                section1 = dict(
                    start=abs_start,
                    end=max_section_width,
                    id=section_id,
                    hour=-start_row,
                )
                section1["start_ts"] = to_dt(
                    abs_start - (max_section_width * start_row)
                )
                section1["end_ts"] = to_dt(max_section_width)
                section1["hour"] = -start_row
                section1["id"] = section_id

                section2 = dict(
                    start=0,
                    end=abs_end - (max_section_width * end_row),
                    id=section_id,
                    hour=-end_row,
                )
                section2["start_ts"] = to_dt(0)
                section2["end_ts"] = to_dt(abs_end - (max_section_width * end_row))
                section2["hour"] = -end_row
                section2["duration"] = section2["end"]
                section2["id"] = section_id
                logger.debug(f"New Section1 {section1}")
                logger.debug(f"New Section2 {section2}")

                section1["start_string"] = start_string
                section1["end_string"] = end_string
                section2["start_string"] = start_string
                section2["end_string"] = end_string
                section1["duration"] = abs_end - abs_start
                section2["duration"] = section1["duration"]
                graph_sections.append(section1)
                graph_sections.append(section2)

        return graph_sections

    logger.error(f"Current Selection: {current_selection.value}")
    formatted_sections = format_sections()
    fig = px.timeline(
        formatted_sections,
        x_start="start_ts",
        x_end="end_ts",
        y="hour",
        range_x=[to_dt(0), to_dt(max_section_width)],
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
    for sect in sections:
        if current_selection.value.id == sect.id:
            fig.add_vline(x=to_dt(sect.start), line_dash="dash", line_color="red")
            fig.add_vline(x=to_dt(sect.end), line_dash="dash", line_color="red")

    def handle_click(*args, **kwargs):
        logger.error(f"Graph Component Clicked args={args}")
        pindex = args[0]["points"]["point_indexes"][0]
        logger.debug(f"Point Index: {pindex}")
        on_click(formatted_sections[pindex])

    solara.FigurePlotly(fig, on_click=handle_click, on_hover=handle_hover)
