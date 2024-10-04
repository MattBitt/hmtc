from typing import Callable

import reacton.ipyvuetify as v
import solara
import solara.lab
from loguru import logger

from archive.oldjellyfin_panel import JellyfinPanel
from hmtc.components.album.album_info import AlbumInfo
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.section import Section, SectionManager
from hmtc.schemas.video import VideoItem

"""
This was my original attempt at a Section Editor Page. It has been replaced by the
newer version in sections.py. I am keeping this here for reference.

"""
update_page = solara.reactive(False)

title = "Video Sections"
MIN_SECTION_LENGTH = 60
MAX_SECTION_LENGTH = 1200


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        raise ValueError("No video selected")

    return router.parts[level:][0]


def compute_section_width(duration):
    if duration < 300:
        return 300
    elif duration < 900:
        return 900
    else:
        return 1800


def compute_graph_dimensions(duration):
    width = compute_section_width(duration)
    height = duration // width
    return width, height


def format_string(x: int):
    if x == 0:
        return "00:00:00"
    h, m, s = x // 3600, (x % 3600) // 60, x % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def create_hms_dict(seconds):
    # created on 9/4/24
    # used by video-sections page for input and
    # label (seconds in milliseconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return dict(
        hour=h,
        minute=m,
        second=s,
    )


@solara.component_vue("../components/shared/carousel.vue")
def Carousel(children=[], model=0):
    pass


@solara.component
def VideoInfo(video, refreshing):
    h, m, s = video.duration // 3600, (video.duration % 3600) // 60, video.duration % 60
    duration_string = f"{h:02d}:{m:02d}:{s:02d}"

    solara.Markdown(f"### {video.title}")

    with solara.Row(justify="space-between"):
        solara.Markdown(f"#### Duration: **{duration_string}** ({video.duration})")
        solara.Button("Refresh", on_click=lambda: refreshing.set(True))
        solara.Button(
            icon_name="mdi-youtube",
            icon=True,
            href=video.url,
        )


@solara.component
def SectionControlPanel(
    video,
    sections,
    current_section,
    on_new: Callable[[Section], None],
    loading: solara.Reactive[bool],
    on_delete: Callable[[Section], None],
):
    section_type = solara.use_reactive("intro")

    # existing sections
    num_sections = solara.use_reactive(len(sections))

    # text box for number of sections
    num_sections_input = solara.use_reactive(4)

    def delete_sections():
        for section in sections:
            on_delete(section)

    def clear_all_sections():
        delete_sections()

    def create_1_section():
        sm = SectionManager.from_video(video)
        sm.create_section(start=0, end=video.duration, section_type=section_type.value)

    def split_into():
        # loading.set(False)
        if num_sections_input.value < 1:
            logger.error("Must have at least 1 section")
            return

        section_length = video.duration // num_sections_input.value
        if section_length < MIN_SECTION_LENGTH:
            logger.error(f"Sections must be at least {MIN_SECTION_LENGTH} seconds long")
            return
        elif section_length > MAX_SECTION_LENGTH:
            logger.error(
                f"Sections must be less than {MAX_SECTION_LENGTH} seconds long"
            )
            return
        num_new_sections = video.duration // section_length
        for i in range(num_new_sections):
            on_new(
                video=video,
                start=i * (video.duration / num_new_sections),
                end=(i + 1) * (video.duration / num_new_sections),
                section_type="intro",
            )

    with solara.Column():
        if num_sections.value > 0:
            solara.Markdown(
                f"Section ID {current_section.value.id if current_section is not None else "asdf"} selected ({num_sections.value } found)"
            )
            solara.Button(
                "Clear All Sections", on_click=clear_all_sections, classes=["button"]
            )
        else:
            solara.Button(
                "Single Section", on_click=create_1_section, classes=["button"]
            )
            with solara.Row():
                solara.InputInt("How Many Sections?", value=num_sections_input)
                solara.Button(
                    "Split",
                    on_click=split_into,
                    classes=["button"],
                )


@solara.component_vue("../components/digits/digit_label.vue", vuetify=True)
def DigitLabel(
    label="default label for DigitalLabel",
    timestamp=dict(id=159, timestamp=12),
    event_enable_editing: Callable[[dict], None] = lambda data: logger.error(
        f"Default Function Call= {data}"
    ),
):
    pass


@solara.component_vue("../components/digits/digit_input.vue", vuetify=True)
def DigitInput(
    label="default label for DigitalInput",
    timestamp=dict(hour=1, minute=2, second=3),
    current_section: solara.Reactive[Section] = None,
):
    pass


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionTimeLine(
    timestamps=dict(
        whole_start=0,
        whole_end=2447,
        part_start=600,
        part_end=1200,
    ),
):
    pass


@solara.component_vue("../components/section/time_edit_form.vue", vuetify=True)
def TimeEditForm(
    section,
    timestamp,
    section_type,
    event_handle_close: Callable[[dict], None],
    event_handle_save: Callable[[dict], None],
    event_adjust_section: Callable[[dict], None],
    counter: int = 187,
):
    pass


def section_modal(section, section_type, model, on_model, video_duration):
    def h_close(*args):
        # logger.debug(f"Closing {args}")
        on_model(False)

    def h_save(*args):
        # logger.debug(f"Saving {args}")
        on_model(False)

    def adjust_section(*args):
        # these should be config values
        # example args[0] = 'large_backward' or 'small_forward'
        if "large" in args[0]:
            increment = 5000
        elif "small" in args[0]:
            increment = 1000
        elif "tiny" in args[0]:
            increment = 250
        else:
            raise ValueError("Invalid adjustment")

        if "back" in args[0]:
            increment = -increment

        logger.debug(
            f"Adjusting the {section_type} of section {section} by {increment} seconds"
        )

        if section_type == "start":
            if section.value.start + increment < 0:
                logger.error("Cannot have negative start time")
                return
            if section.value.start + increment >= section.value.end:
                logger.error("Start time must be before end time")
                return

            SectionManager.edit_section_start(
                section=section.value, increment=increment
            )

        else:
            if section.value.end + increment > video_duration:
                logger.error("Cannot have end time past video duration")
                return
            if section.value.end + increment <= section.value.start:
                logger.error("End time must be after start time")
                return
            SectionManager.edit_section_end(section=section.value, increment=increment)

        logger.debug("Adjustment complete. About to refresh the sections")

    if section_type == "start":
        ts = create_hms_dict(section.value.start // 1000)
    else:
        ts = create_hms_dict(section.value.end // 1000)

    with v.Dialog(
        v_model=model,
        on_v_model=on_model,
        persistent=True,
        max_width="80%",
    ):
        TimeEditForm(
            section=dict(
                id=section.value.id, start=section.value.start, end=section.value.end
            ),
            timestamp=ts,
            section_type=section_type,
            event_handle_close=lambda data: h_close(data),
            event_handle_save=lambda data: h_save(data),
            event_adjust_section=lambda data: adjust_section(data),
        )


@solara.component
def SectionTimeInfo(video, section, refresh_sections):
    edit_start, set_edit_start = solara.use_state(False)
    edit_end, set_edit_end = solara.use_state(False)
    solara.use_reactive(0)
    solara.use_reactive(create_hms_dict(section.value.start // 1000))
    solara.use_reactive(create_hms_dict(section.value.end // 1000))

    # these modals are controlled by the model and on_model reactive variables
    section_modal(
        section=section,
        section_type="start",
        model=edit_start,
        on_model=set_edit_start,
        video_duration=video.duration,
    )
    section_modal(
        section=section,
        section_type="end",
        model=edit_end,
        on_model=set_edit_end,
        video_duration=video.duration,
    )

    with solara.Row(justify="space-around"):
        with solara.Column():
            DigitLabel(
                label="Start Time",
                timestamp=create_hms_dict(section.value.start // 1000),
            )
            solara.Button(
                label="Open Section Modal",
                icon_name="mdi-pencil",
                on_click=lambda: set_edit_start(True),
                classes=["button"],
            )
        with solara.Column():
            solara.Markdown(f"### Section {section.value.id}")
            solara.Markdown(f"### Start {section.value.start} End {section.value.end}")
            DigitLabel(
                label="End Time",
                timestamp=create_hms_dict(section.value.end // 1000),
            )
            solara.Button(
                label="Open Section Modal",
                icon_name="mdi-pencil",
                on_click=lambda: set_edit_end(True),
                classes=["button"],
            )


@solara.component
def TopicInput(new_topic, on_click_func):
    with solara.Row():
        solara.InputText(label="Topic", value=new_topic)
        (solara.Button(label="Add Topic", on_click=on_click_func),)


@solara.component_vue("../components/section/topics_list.vue", vuetify=True)
def SectionTopicsList(section, topics=["Topic 1", "Topic 2", "Topic 3"]):
    pass


# @solara.component
# def SectionTopics(section: solara.Reactive[Section]):
#     new_topic = solara.use_reactive("")
#     topics = solara.use_reactive(["football", "cats", "dogs"])

#     def add_topic():
#         if new_topic.value:
#             topics.value.append(new_topic.value)
#             new_topic.value = ""

#     with solara.Card():
#         TopicInput(new_topic=new_topic, on_click_func=add_topic)
#         TopicsList(topics=topics.value)


class State:
    @staticmethod
    def on_new(video, start: int, end: int, section_type: str):
        logger.debug(f"Adding new item: {start}, {end}, {section_type}")
        sm = SectionManager.from_video(video)
        sm.create_section(start=start, end=end, section_type=section_type)

    @staticmethod
    def on_delete(item: Section):
        logger.debug(f"Deleting item: {item}")
        SectionManager.delete_from_db(item)


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    sections = solara.use_reactive(Section.from_video(video))
    # width, height = compute_graph_dimensions(video.duration)

    model = solara.use_reactive(0)
    solara.use_reactive(["flying", "kangaroo", "flag"])

    def next_slide():
        if model.value == len(sections.value) - 1:
            model.set(0)
        else:
            model.set(model.value + 1)

    def prev_slide():
        if model.value == 0:
            model.set(len(sections.value) - 1)
        else:
            model.set(model.value - 1)

    def refresh_sections():
        logger.debug("Refreshing sections")
        sects = Section.from_video(video)
        logger.debug("Sections: {sects}")
        sections.set(sects)

    with solara.Column(classes=["main-container"]):
        with solara.Row():
            with solara.Column():
                with solara.Card(title=f"{model.value}"):
                    VideoInfo(video, refreshing=False)
                    # AlbumInfo(video)

                with solara.Card():
                    SectionControlPanel(
                        video=video,
                        sections=sections.value,
                        current_section=None,
                        on_new=State.on_new,
                        loading=False,
                        on_delete=State.on_delete,
                    )
            # with solara.Card(style="width: 30%"):
            #     JellyfinPanel(
            #         current_video_youtube_id=video.youtube_id,
            #         current_section=None,
            #         status=dict(connected=False, correct_video=False),
            #     )
        # with solara.Card():
        #     SectionGraphComponent(
        #         formatted_sections=format_sections(
        #             sections, selected_index=model.value
        #         ),
        #         on_click=lambda data: model.set(data),
        #         max_section_width=width,
        #         max_section_height=height,
        #     )
        if update_page.value:
            logger.debug("Updating page")
            update_page.set(False)
        else:
            with solara.Card():
                with solara.Column():
                    with solara.Row(justify="space-between"):
                        solara.Button(
                            "Previous", on_click=prev_slide, classes=["button"]
                        )
                        solara.Markdown(
                            f"## Section {model.value + 1} of {len(sections.value)}"
                        )
                        solara.Button("Next", on_click=next_slide, classes=["button"])
                    with solara.Column():
                        if len(sections.value) > 0:
                            SectionTimeLine(
                                timestamps=dict(
                                    whole_start=0,
                                    whole_end=video.duration,
                                    part_start=sections.value[model.value].start
                                    // 1000,
                                    part_end=sections.value[model.value].end // 1000,
                                )
                            )
                        else:
                            solara.Markdown("No Sections Found")

                    with Carousel(model=model.value):
                        for section in sections.value:
                            s = solara.use_reactive(section)
                            with solara.Column():
                                SectionTimeInfo(
                                    video=video,
                                    section=s,
                                    refresh_sections=refresh_sections,
                                )
