import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from dataclasses import asdict
from typing import Callable
from loguru import logger
import reacton.ipyvuetify as v
from hmtc.models import Video
from hmtc.models import Section as SectionTable
import solara
from solara.lab.toestand import Ref
import time
from hmtc.mods.section import SectionManager, Section
import numpy as np
import plotly.express as px
import pandas as pd
import solara
import plotly.graph_objects as go
from ipywidgets import Output, VBox

x = np.linspace(0, 2, 100)

title = "HMTC Section Editor"
freq = solara.reactive(2.0)
phase = solara.reactive(0.1)

import numpy as np

seed = solara.reactive(42)

out = Output()


@out.capture(clear_output=True)
def handle_click(trace, points, state):
    logger.error("are you there? AHHHHHHHHH 😱😱😱")
    print(points.point_inds)


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        raise ValueError("No video selected")

    return router.parts[level:][0]


@solara.component
def SectionEdit(
    section_item: solara.Reactive[Section],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    """Takes a reactive section item and allows editing it. Will not modify the original item until 'save' is clicked."""
    copy = solara.use_reactive(section_item.value)

    def save():
        section_item.value = copy.value
        on_close()

    with solara.Card("Edit", margin=0):
        solara.InputText(label="ID", value=Ref(copy.fields.id), disabled=True)
        with solara.CardActions():
            v.Spacer()
            solara.Button(
                "Save",
                icon_name="mdi-content-save",
                on_click=save,
                outlined=True,
                text=True,
            )
            solara.Button(
                "Close",
                icon_name="mdi-window-close",
                on_click=on_close,
                outlined=True,
                text=True,
            )
            solara.Button(
                "Delete",
                icon_name="mdi-delete",
                on_click=on_delete,
                outlined=True,
                text=True,
            )


@solara.component_vue("section_bargraph_item.vue")
def SectionBarGraphItem(
    event_goto_report: Callable[[dict], None],
    value=[1, 10, 30, 20, 3],
    caption="My Card",
    color="red",
):
    pass


@solara.component_vue("section_slide.vue", vuetify=True)
def SectionSlide(
    section_speak: Callable[[dict], None],
    avalue="mizzle",
    slides=[],
):

    pass


@solara.component
def SectionListItem(
    section_item: solara.Reactive[Section],
    video,
    is_selected: bool,
    on_delete: Callable[[Section], None],
    change_section_type: Callable[[Section], None],
):
    edit, set_edit = solara.use_state(False)

    def delete():
        State.loading.value = True
        on_delete(section_item.value)
        State.loading.value = False

    width = (section_item.value.end - section_item.value.start) / video.duration * 100
    # style=f"width: {width}% height: 800px", margin=0
    if is_selected:
        border = "4px solid red"
    else:
        border = "4px solid green"

    with solara.Card(style=f"border: {border}", margin=0):
        solara.InputInt(label="ID", value=section_item.value.id)
        solara.Markdown(
            f"**time**: {(section_item.value.end - section_item.value.start)}"
        )
        solara.Markdown(f"Width: {width}%")

        solara.InputInt(label="Start", value=section_item.value.start)
        solara.InputInt(label="End", value=section_item.value.end)
        solara.InputText(
            label="Section Type", value=Ref(section_item.fields.section_type)
        )
        with solara.CardActions():
            solara.Button(
                icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
            )
            solara.Button(
                icon_name="mdi-delete",
                icon=True,
                on_click=delete,
            )
            solara.Button(
                icon_name="mdi-axis-x-arrow",
                tooltip="Change to instrumental",
                icon=True,
                on_click=lambda: change_section_type(
                    section_item.value, "instrumental"
                ),
            )
        with v.Dialog(
            v_model=edit, persistent=True, max_width="500px", on_v_model=set_edit
        ):
            if edit:  # 'reset' the component state on open/close

                def on_delete_in_edit():
                    on_delete(section_item.value)
                    set_edit(False)

                SectionEdit(
                    section_item,
                    on_delete=on_delete_in_edit,
                    on_close=lambda: set_edit(False),
                )


@solara.component
def SectionControlPanel(
    video,
    on_new: Callable[[Section], None],
    loading: solara.Reactive[bool],
    on_delete: Callable[[Section], None],
):

    start = solara.reactive(0)
    end = solara.reactive(video.duration)
    section_type = solara.reactive("intro")

    def add_section():
        loading.value = True
        on_new(
            video=video,
            start=start.value,
            end=end.value,
            section_type=section_type.value,
        )
        loading.value = False

    num_sections = solara.use_reactive(2)

    def delete_sections():
        for section in video.sections:
            on_delete(section)

    def clear_sections():
        loading.value = True
        delete_sections()
        loading.value = False

    def split():

        logger.error(f"Splitting {video.title} into {num_sections.value} sections")
        logger.error(
            f"Each section will be { video.duration / num_sections.value} seconds long"
        )
        delete_sections()
        for i in range(num_sections.value):
            on_new(
                video=video,
                start=i * (video.duration / num_sections.value),
                end=(i + 1) * (video.duration / num_sections.value),
                section_type="intro",
            )

    def split_into_1():
        loading.value = True
        num_sections.value = 1
        split()
        loading.value = False

    def split_into_2():
        loading.value = True
        num_sections.value = 2
        split()
        loading.value = False

    def split_into_10():
        loading.value = True
        num_sections.value = 10
        split()
        loading.value = False

    def split_into_40():
        loading.value = True
        num_sections.value = 40
        split()
        loading.value = False

    with solara.Column():
        solara.Markdown("#### Clear and Create Sections")
        with solara.Row():
            solara.Button("1", on_click=split_into_1)
            solara.Button("2", on_click=split_into_2)
            solara.Button("10", on_click=split_into_10)
            solara.Button("40", on_click=split_into_40)
            solara.Button("Clear All Sections", on_click=clear_sections)


### Don't know if this is true, but should be when finished
### reusable above this line
### below this line is the page definition


class State:
    loading = solara.reactive(False)

    @staticmethod
    def load_sections(video_id: int):
        logger.warning(f"Loading sections (from page 31) for video: {video_id}")
        video = Video.get_by_id(video_id)
        sm = SectionManager.from_video(video)
        State.sections = solara.use_reactive(sm.sections)
        if State.sections.value:
            initial = State.sections.value[0]
        else:
            initial = None
        State.selected_section = solara.reactive(initial)

    @staticmethod
    def on_new(video, start: int, end: int, section_type: str):

        logger.debug(f"Adding new item: {start}, {end}, {section_type}")
        sm = SectionManager.from_video(video)
        sm.create_section(start=start, end=end, section_type=section_type)
        State.sections.value = sm.sections

        logger.debug(
            f"after adding: ({len(State.sections.value)}){State.sections.value}"
        )

    @staticmethod
    def on_delete(item: Section):
        logger.debug(f"Deleting item: {item}")
        new_items = list(State.sections.value)
        new_items.remove(item)
        SectionManager.delete_from_db(item)
        State.sections.value = new_items

    @staticmethod
    def change_section_type(item: Section, new_type: str):
        State.loading.value = True
        logger.debug(f"Changing section type of item: {item}")
        new_items = list(State.sections.value)
        new_items.remove(item)
        item.section_type = "instrumental"
        new_items.append(item)
        sect = SectionTable.select().where(SectionTable.id == item.id).get()
        sect.section_type = "instrumental"
        sect.save()
        State.sections.value = new_items
        State.loading.value = False


@solara.component
def SectionStatus():
    """Status of our section list"""
    items = State.sections.value

    count = len(items)
    # solara.Info(f"{count} item{'s' if count != 1 else ''} total")
    # solara.Error(f"Sections: {[x.id for x in items]}")


@solara.component
def VideoInfo(video):
    h, m, s = video.duration // 3600, (video.duration % 3600) // 60, video.duration % 60
    duration_string = f"{h:02d}:{m:02d}:{s:02d}"
    with solara.Column():
        solara.Markdown(f"## {video.title}")

        solara.Markdown(f"#### Duration: **{duration_string}**")
        solara.Button(
            icon_name="mdi-youtube",
            icon=True,
            href=video.url,
        )


@solara.component
def VueComponent():
    gen = np.random.RandomState(seed=seed.value)
    n = np.random.RandomState(seed=seed.value)
    sales_data = np.floor(np.cumsum(gen.random(7) - 0.5) * 100 + 100)
    show_report = solara.use_reactive(False)

    def goto_report():
        show_report.set(True)

    with solara.Column():
        if show_report.value:
            with solara.Card("Report"):
                solara.Markdown("Lorum ipsum dolor sit amet")
                solara.Button("Go back", on_click=lambda data: show_report.set(False))
        else:

            def new_seed():
                seed.value = np.random.randint(0, 100)

            solara.Button("Generate new data", on_click=new_seed)
            SectionBarGraphItem(
                value=sales_data.tolist(),
                color="blue",
                caption="Sales Last 7 Days",
                event_goto_report=goto_report,
            )


@solara.component
def GraphComponent(video, selected_section: solara.Reactive[Section]):
    # if video.sections.count() == 0:
    #     SectionManager.from_video(video).create_section(0, video.duration, "INITIAL")
    def handle_click(*args, **kwargs):
        logger.error(f"Click occured at index: {args[0]['points']['point_indexes']}")
        logger.debug(f"args: {args}")
        logger.debug(f"kwargs: {kwargs}")
        start = pd.Timestamp(args[0]["points"]["xs"][0])
        sect = (
            SectionTable.select()
            .where(
                (SectionTable.start == start.timestamp())
                & (SectionTable.video_id == video.id)
            )
            .get_or_none()
        )
        logger.error(f"SectionTable query result: {sect}")
        if sect:
            State.selected_section.value = sect
        else:
            logger.error("No section found🧬🧬🧬")

    def handle_hover(*args, **kwargs):
        logger.error(f"Hover occured at index: {args[0]['points']['point_indexes']}")
        logger.debug(f"args: {args}")
        logger.debug(f"kwargs: {kwargs}")

    section_list = []
    for sect in video.sections:

        h, m, s = sect.start // 3600, (sect.start % 3600) // 60, sect.start % 60
        start_str = f"{h:02d}:{m:02d}:{s:02d}"
        h, m, s = sect.end // 3600, (sect.end % 3600) // 60, sect.end % 60
        end_str = f"{h:02d}:{m:02d}:{s:02d}"

        section_list.append(
            dict(
                id=sect.id,
                start=pd.to_datetime(sect.start, utc=True, unit="s"),
                end=pd.to_datetime(sect.end, utc=True, unit="s"),
                section_type=sect.section_type,
                start_str=start_str,
                end_str=end_str,
                row=1,
            ),
        )

    df = pd.DataFrame(section_list)
    x_rmin = pd.to_datetime(0, utc=True, unit="s")
    x_rmax = pd.to_datetime(video.duration, utc=True, unit="s")
    timeline = px.timeline(
        df, x_start="start", x_end="end", y="row", hover_data=["section_type"]
    )

    fig = make_subplots()

    layout = timeline["layout"]
    fig.layout = layout

    data = timeline["data"][0]

    data["marker"]["color"] = df["section_type"].map(
        {
            "intro": "orange",
            "instrumental": "green",
            "acapella": "yellow",
            "outro": "blue",
        }
    )

    fig.add_trace(data)

    logger.error(f"x_rmin: {x_rmin}")
    logger.error(f"x_rmax: {x_rmax}")
    logger.error(f"Section Duration: {datetime.timedelta(seconds=video.duration)}")
    x_range = [x_rmin, x_rmax]

    fig.update_layout(
        template="plotly_dark",
        barmode="overlay",
        height=150,
        margin=dict(l=0, r=0, t=0, b=0),
        title_text="Section Timeline",
        xaxis=dict(
            position=0,
            title="time",
            range=x_range,
            tickfont=dict(size=12),
            tickformat="%H:%M:%S",
        ),
        yaxis=dict(
            title_text="",
            tickvals=[],
            tickmode="array",
        ),
    )
    solara.FigurePlotly(fig, on_click=handle_click, on_hover=handle_hover)


@solara.component
def Page():

    def t_logger():
        logger.error("💡💡💡 Testing the Logger 💡💡💡")

    video_id = parse_url_args()
    State.load_sections(video_id)
    video = Video.get_by_id(video_id)
    if video.duration == 0:
        solara.Error("Video has no duration. Please Refresh from youtube.")

        return
    with solara.Columns(6, 6):
        VideoInfo(video)
        SectionControlPanel(
            video=video,
            on_new=State.on_new,
            loading=State.loading,
            on_delete=State.on_delete,
        )

    if State.loading.value:
        solara.SpinnerSolara()
    else:
        if video.sections.count() == 0:
            solara.Markdown("## No Sections Found. Please add some.")
            return

        with solara.Column():
            SectionStatus()
            with solara.Column():
                # VueComponent()
                GraphComponent(video, selected_section=Ref(State.selected_section))

        # h, m, s = sect.start // 3600, (sect.start % 3600) // 60, sect.start % 60
        # start_str = f"{h:02d}:{m:02d}:{s:02d}"
        # h, m, s = sect.end // 3600, (sect.end % 3600) // 60, sect.end % 60
        # end_str = f"{h:02d}:{m:02d}:{s:02d}"

        def format_string(x):
            h, m, s = x // 3600, (x % 3600) // 60, x % 60
            return f"{h:02d}:{m:02d}:{s:02d}"

        sects = [
            dict(
                id=x.id,
                start=x.start,
                end=x.end,
                section_type=x.section_type,
                start_str=format_string(x.start),
                end_str=format_string(x.end),
                row=1,
                description=video.description,
            )
            for x in State.sections.value
        ]
        with solara.Column():
            solara.Markdown("")
        SectionSlide(slides=sects)
        logger.error(f"Currently selected: {State.selected_section.value}")

        # with solara.Row():
        #     for index, item in enumerate(State.sections.value):
        #         section_item = Ref(State.sections.fields[index])
        #         is_selected = State.selected_section.value == section_item.value

        #         SectionListItem(
        #             section_item,
        #             is_selected=is_selected,
        #             video=video,
        #             on_delete=State.on_delete,
        #             change_section_type=State.change_section_type,
        #         )
