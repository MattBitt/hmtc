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
from hmtc.components.section.section_graph import SectionGraphComponent

title = "HMTC Section Editor"


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        raise ValueError("No video selected")

    return router.parts[level:][0]


def format_string(x):
    if x == 0:
        return "00:00:00"
    h, m, s = x // 3600, (x % 3600) // 60, x % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


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


@solara.component_vue("mycard2.vue")
def MyCard2(
    event_button_click: Callable[[dict], None],
    event_set_start_time: Callable[[str], None],
    event_set_end_time: Callable[[str], None],
    event_set_section_type: Callable[[str], None],
    section=dict(id=15, start="00:00:00", end="23:59:59"),
):
    pass


@solara.component_vue("section_carousel.vue", vuetify=True)
def SectionCarouselVue(
    event_first_event,
    slides=[],
):

    pass


@solara.component_vue("section_slide_group.vue", vuetify=True)
def SectionSlideGroupVue():

    pass


@solara.component
def SectionCarousel(
    slides,
    selected_section: solara.Reactive[Section],
    event_first_event: Callable[[dict], None],
):
    start_time = solara.use_reactive(selected_section.value.start)
    end_time = solara.use_reactive(selected_section.value.end)
    section_type = solara.use_reactive(selected_section.value.section_type)

    def first_event(*args):
        logger.debug(f"First event called with args: {args}")
        event_first_event(args[0])

    # if selected_section.value is None:
    #     State.select_section(slides[0])

    def complicated_function(*args):
        logger.error(f"Args = {args}")
        return args[0]

    def set_section_type(*args):
        logger.error(f"Args = {args}")
        return args[0]

    with solara.Column(style={"min-width": "600px"}):
        # solara.Markdown(f"Current Selection: {selected_section.value}")
        MyCard2(
            section=dict(
                id=selected_section.value.id,
                start=start_time.value,
                end=end_time.value,
                is_first=True,
                is_last=True,
                section_type=section_type.value,
                start_string=format_string(start_time.value),
                end_string=format_string(end_time.value),
            ),
            event_set_start_time=lambda data: start_time.set(
                complicated_function(data)
            ),
            event_set_end_time=lambda data: end_time.set(complicated_function(data)),
            event_set_section_type=lambda data: section_type.set(
                set_section_type(data)
            ),
        )

    # for slide in slides:
    #     if selected_section.value is not None:
    #         if slide["id"] == selected_section.value.id:
    #             solara.Success(f"Selected: {slide['id']}")
    #             slide["selected"] = True
    # SectionCarouselVue(slides=slides, event_first_event=first_event)


current_selection = solara.reactive(None)


@solara.component
def VideoInfo(video: solara.Reactive[Section]):
    h, m, s = video.duration // 3600, (video.duration % 3600) // 60, video.duration % 60
    duration_string = f"{h:02d}:{m:02d}:{s:02d}"
    with solara.Column():
        solara.Markdown(f"## {video.title}")
        with solara.Row(justify="space-between"):
            solara.Markdown(f"#### Duration: **{duration_string}**")
            with solara.Column():
                solara.Markdown("Section ID")

        solara.Button(
            icon_name="mdi-youtube",
            icon=True,
            href=video.url,
        )


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

        logger.debug(f"Splitting {video.title} into {num_sections.value} sections")
        logger.debug(
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
    selected_section = solara.reactive(None)

    @staticmethod
    def load_sections(video_id: int):

        video = Video.get_by_id(video_id)
        sm = SectionManager.from_video(video)
        if State.selected_section.value is None:
            sect = (
                SectionTable.select().where(SectionTable.id == video_id).get_or_none()
            )
            if sect:
                State.selected_section.value = sect
            else:
                logger.debug("No section found🧬🧬🧬")
                State.selected_section.value = None
        State.sections = solara.use_reactive(sm.sections)

        if State.selected_section.value is None and len(State.sections.value) > 0:
            State.select_section(State.sections.value[0])

            logger.warning(f"Video Section State Init for Video: {video_id}")

    @staticmethod
    def on_new(video, start: int, end: int, section_type: str):

        # logger.debug(f"Adding new item: {start}, {end}, {section_type}")
        sm = SectionManager.from_video(video)
        sm.create_section(start=start, end=end, section_type=section_type)
        State.sections.value = sm.sections

        # logger.debug(
        #     f"after adding: ({len(State.sections.value)}){State.sections.value}"
        # )

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

    @staticmethod
    def select_section(item: Section):
        State.loading.value = True
        State.selected_section.value = item
        State.loading.value = False


@solara.component
def GraphComponent(video, selected_section: solara.Reactive[Section]):
    # if video.sections.count() == 0:
    #     SectionManager.from_video(video).create_section(0, video.duration, "INITIAL")
    def handle_click(*args, **kwargs):
        logger.error(f"Click occured at index: {args[0]['points']['point_indexes']}")
        logger.debug(f"args: {args}")
        logger.debug(f"kwargs: {kwargs}")
        start = ["points"]["xs"][0]
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
            State.select_section(sect)
        else:
            logger.error("No section found🧬🧬🧬")

    def handle_hover(*args, **kwargs):
        # logger.error(f"Hover occured at index: {args[0]['points']['point_indexes']}")
        # logger.debug(f"args: {args}")
        # logger.debug(f"kwargs: {kwargs}")
        pass

    def seconds_to_hms_val(seconds):
        if seconds == 0:
            return 0, 0, 0

        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        return h, m, s

    def seconds_to_hms_str(seconds):
        logger.error(f"Checking seconds in seconds_to_hms_str: {seconds}")
        if seconds == 0:
            return "00:00:00"
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def get_hour_from_seconds(seconds):
        return seconds // 3600

    def prep_sections_for_graph(video):
        section_list = []
        for sect in video.sections:
            start_str = seconds_to_hms_str(sect.start)
            end_str = seconds_to_hms_str(sect.end)

            base_section = dict(
                id=sect.id,
                section_type=sect.section_type,
                start_str=start_str,
                end_str=end_str,
                selected=False,
            )

            sh, sm, ss = seconds_to_hms_val(sect.start)
            eh, em, es = seconds_to_hms_val(sect.end)

            if sh == eh:
                # only one section on the graph needed
                if sh > 0:
                    s = sect.start - (sh * 3600)
                    e = sect.end - (sh * 3600)
                else:
                    s = sect.start
                    e = sect.end
                new_section = dict(
                    **base_section,
                    start=s,
                    end=e,
                    duration=e - s,
                    row=100,
                )
                section_list.append(new_section)
            else:
                # around the horn
                if eh - sh > 1:
                    solara.Info("Section spans more than 1 hour. Not supported.")
                    return
                start = sect.start
                end = sh * 3600
                new_section1 = dict(
                    **base_section,
                    start=start,
                    end=end,
                    duration=end - start,
                    row=100,
                )

                start = 0
                end = sect.end * 3600
                new_section2 = dict(
                    **base_section,
                    start=start,
                    end=end,
                    duration=end - start,
                    row=100,
                )
                section_list.append(new_section1)
                section_list.append(new_section2)

        return section_list

    graph_sections = prep_sections_for_graph(video)

    df = pd.DataFrame(graph_sections)
    x_rmin = 0
    if video.duration > 3600:
        x_rmax = 3800
    elif video.duration > 1800:
        x_rmax = 1900
    elif video.duration > 1500:
        x_rmax = 1600
    elif video.duration > 300:
        x_rmax = video.duration + 100
    else:
        x_rmax = video.duration

    x_range = [x_rmin, x_rmax]

    bar_graph = px.bar(
        df,
        x="start",
        y="row",
        hover_data=["id", "start", "end", "duration"],
        height=300,
        orientation="h",
    )
    x_vals = df["start"].tolist()
    x_vals.append(df["end"].max())
    y_vals = df["row"].tolist()
    logger.error(f"X Vals: {x_vals}")
    logger.error(f"Y Vals: {y_vals}")

    fig = go.Figure(go.Bar(x=x_vals, y=y_vals, orientation="h"))

    # fig = make_subplots()

    layout = bar_graph["layout"]
    fig.layout = layout

    data = bar_graph["data"][0]

    data["marker"]["color"] = df["section_type"].map(
        {
            "intro": "orange",
            "instrumental": "green",
            "acapella": "yellow",
            "outro": "blue",
        }
    )

    fig.add_trace(data)

    logger.debug(f"x_rmin: {x_rmin}")
    logger.debug(f"x_rmax: {x_rmax}")
    logger.debug(f"Section Duration: {datetime.timedelta(seconds=video.duration)}")

    fig.update_layout(
        template="plotly_dark",
        title_text="Section Timeline",
        xaxis=dict(
            position=0,
            title="time",
            range=x_range,
            tickfont=dict(size=12),
            tickformat="%H:%M:%S",
        ),
        # yaxis=dict(
        #     title_text="",
        #     tickvals=[],
        #     tickmode="array",
        # ),
    )
    solara.FigurePlotly(fig, on_click=handle_click, on_hover=handle_hover)


@solara.component
def Page():

    video_id = parse_url_args()
    State.load_sections(video_id)

    video = Video.get_by_id(video_id)
    if video.duration == 0:
        solara.Error("Video has no duration. Please Refresh from youtube.")
        return

    # package the section info for the section carousel
    carousel_sections = [
        dict(
            id=x.id,
            start=x.start,
            end=x.end,
            section_type=x.section_type,
            start_str=format_string(x.start),
            end_str=format_string(x.end),
        )
        for x in State.sections.value
    ]

    with solara.Columns(6, 6):
        VideoInfo(video)
        SectionControlPanel(
            video=video,
            on_new=State.on_new,
            loading=State.loading,
            on_delete=State.on_delete,
        )

    def afunc(*args):
        logger.debug(f"afunc called with data: {args}")
        id = args[0]
        logger.debug(f"ID: {id}")
        sect = SectionTable.select().where(SectionTable.id == id).get()
        if sect:
            State.select_section(sect)
        else:
            logger.debug("No section found🧬🧬🧬")

    def on_click(*args):
        logger.debug(f"on_click called with data: {args}")
        id = args[0]["id"]
        logger.debug(f"ID: {id}")
        sect = SectionTable.select().where(SectionTable.id == id).get()
        if sect:
            State.select_section(sect)
        else:
            logger.debug("No section found🧬🧬🧬")

    with solara.Column():
        if State.loading.value:
            solara.SpinnerSolara(size="100px")
        else:
            if video.sections.count() == 0:
                solara.Markdown("## No Sections Found. Please add some.")
                return
            if video.duration < 1800:
                section_width = video.duration
            elif video.duration < 3600:
                section_width = video.duration / 2
            else:
                section_width = 1800
            if State.selected_section.value is not None:
                solara.InputText(
                    label="Current Selection",
                    value=State.selected_section.value.id,
                )
            SectionGraphComponent(
                video.sections,
                current_selection=Ref(State.selected_section),
                on_click=on_click,
                max_section_width=section_width,
            )
            SectionCarousel(
                slides=carousel_sections,
                selected_section=Ref(State.selected_section),
                event_first_event=afunc,
            )
            with solara.Card():
                solara.Markdown("Current Selection")
                sect = State.selected_section.value
                solara.Markdown(str(sect.id))
                solara.Markdown(str(sect.start))
                solara.Markdown(str(sect.end))
                solara.Markdown("# IT WORKS!")

            logger.error(f"Currently selected: {State.selected_section.value}")
