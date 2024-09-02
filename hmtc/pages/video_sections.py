from typing import Callable

import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.section.section_graph import SectionGraphComponent
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.album.album_info import AlbumInfo
from hmtc.components.shared.jellyfin_panel import JellyfinPanel
from hmtc.models import Video
from hmtc.mods.section import Section, SectionManager
from hmtc.schemas.video import VideoItem


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
    timestamp=dict(id=387, timestamp=1203),
):
    pass


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionLine(
    timestamps=dict(
        whole_start=0,
        whole_end=2447,
        part_start=600,
        part_end=1200,
    )
):
    pass


@solara.component
def SectionTimeButtons(
    small_forward: Callable = None,
    small_backward: Callable = None,
    large_forward: Callable = None,
    large_backward: Callable = None,
):
    with solara.Row(justify="center"):
        solara.Button(
            label="-5",
            icon_name="mdi-step-backward-2",
            on_click=large_backward,
            classes=["button"],
        )
        solara.Button(
            label="-1",
            icon_name="mdi-step-backward",
            on_click=small_backward,
            classes=["button"],
        )
        solara.Button(
            label="+1",
            icon_name="mdi-step-forward",
            on_click=small_forward,
            classes=["button"],
        )

        solara.Button(
            label="+5",
            icon_name="mdi-step-forward-2",
            on_click=large_forward,
            classes=["button"],
        )


@solara.component
def SectionSaveCancel(
    save: Callable = None,
    cancel: Callable = None,
):
    with solara.Row(justify="center"):
        solara.Button(
            label="Save",
            icon_name="mdi-content-save",
            on_click=save,
            classes=["button"],
        )
        solara.Button(
            label="Cancel",
            icon_name="mdi-cancel",
            on_click=cancel,
            classes=["button"],
        )


@solara.component
def SectionTiming(
    current_selection: solara.Reactive[Section],
    _video,
):

    section = current_selection.value

    def section_start_minus_5():
        logger.debug("Section Start Minus 5")
        SectionManager.edit_section_start(section, timestamp=section.start - 5)

    def section_end_minus_5():
        logger.debug("Section Start Minus 5")
        SectionManager.edit_section_end(section, timestamp=section.end - 5)

    editing_start = solara.use_reactive(False)
    editing_end = solara.use_reactive(False)

    h, m, s = section.start // 3600, (section.start % 3600) // 60, section.start % 60
    start = dict(id=15, timestamp=section.start, hour=h, minute=m, second=s)

    h, m, s = section.end // 3600, (section.end % 3600) // 60, section.end % 60
    end = dict(id=37, timestamp=section.end, hour=h, minute=m, second=s)

    video = _video
    timestamps = dict(
        whole_start=0,
        whole_end=video.duration,
        part_start=section.start,
        part_end=section.end,
    )

    with solara.Card(elevation=10, margin="2"):
        with solara.Columns():
            SectionLine(timestamps=timestamps)

        with solara.Columns():
            with solara.Card():
                if editing_start.value:
                    with solara.Column():
                        DigitInput(
                            label="Start Time",
                            timestamp=start,
                        )

                        SectionTimeButtons(
                            small_forward=lambda: logger.debug("Start Small Forward"),
                            small_backward=lambda: logger.debug("Start Small Backward"),
                            large_forward=lambda: logger.debug("Start Large Forward"),
                            large_backward=section_start_minus_5,
                        )
                        SectionSaveCancel(
                            save=lambda: editing_start.set(False),
                            cancel=lambda: editing_start.set(False),
                        )

                else:
                    with solara.Column():
                        DigitLabel(
                            label="Start Time",
                            timestamp=start,
                        )
                        solara.Button(
                            label="Edit",
                            icon_name="mdi-pencil",
                            on_click=lambda: editing_start.set(True),
                            classes=["button"],
                        )
            with solara.Card():
                if editing_end.value:

                    with solara.Column():
                        DigitInput(
                            label="End Time",
                            timestamp=end,
                        )
                        SectionTimeButtons(
                            small_forward=lambda: logger.debug("End Small Forward"),
                            small_backward=lambda: logger.debug("End Small Backward"),
                            large_forward=lambda: logger.debug("End Large Forward"),
                            large_backward=section_end_minus_5,
                        )
                        SectionSaveCancel(
                            save=lambda: logger.error("Save"),
                            cancel=lambda: editing_end.set(False),
                        )
                else:
                    with solara.Column():
                        DigitLabel(
                            label="End Time",
                            timestamp=end,
                            event_enable_editing=lambda data: logger.error(
                                f"Event Enable Editing Called = {data}"
                            ),
                        )
                        solara.Button(
                            label="Edit",
                            icon_name="mdi-pencil",
                            on_click=lambda: editing_end.set(True),
                            classes=["button"],
                        )


@solara.component
def SectionControlPanel(
    video,
    sections,
    current_selection: solara.Reactive[Section],
    on_new: Callable[[Section], None],
    loading: solara.Reactive[bool],
    on_delete: Callable[[Section], None],
):
    start = solara.reactive(0)
    end = solara.reactive(video.duration)
    section_type = solara.reactive("intro")

    # existing sections
    num_sections = solara.reactive(len(sections))

    # text box for number of sections
    num_sections_input = solara.reactive(num_sections)

    def delete_sections():
        for section in video.sections:
            on_delete(section)

    def clear_all_sections():
        loading.value = True
        delete_sections()
        loading.value = False

    def create_1_section():
        loading.value = True
        sm = SectionManager.from_video(video)
        sm.create_section(start=0, end=video.duration, section_type=section_type.value)
        loading.value = False

    def split_into():
        section_length = video.duration // num_sections_input.value
        if section_length < MIN_SECTION_LENGTH:
            logger.error(f"Sections must be at least {MIN_SECTION_LENGTH} seconds long")
            return
        elif section_length > MAX_SECTION_LENGTH:
            logger.error(
                f"Sections must be less than {MAX_SECTION_LENGTH} seconds long"
            )
            return
        loading.set(True)
        num_new_sections = video.duration // section_length
        for i in range(num_new_sections):
            on_new(
                video=video,
                start=i * (video.duration / num_new_sections),
                end=(i + 1) * (video.duration / num_new_sections),
                section_type="intro",
            )
        loading.set(False)

    with solara.Column():
        if num_sections.value > 0:
            solara.Markdown(
                f"Section ID {current_selection.value.id} selected ({num_sections.value } found)"
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


@solara.component
def VideoInfo(video):
    h, m, s = video.duration // 3600, (video.duration % 3600) // 60, video.duration % 60
    duration_string = f"{h:02d}:{m:02d}:{s:02d}"

    solara.Markdown(f"### {video.title}")

    with solara.Row(justify="space-between"):
        solara.Markdown(f"#### Duration: **{duration_string}** ({video.duration})")

        solara.Button(
            icon_name="mdi-youtube",
            icon=True,
            href=video.url,
        )


@solara.component
def TopicInput(new_topic, on_click_func):
    with solara.Row():
        solara.InputText(label="Topic", value=new_topic)
        solara.Button(label="Add Topic", on_click=on_click_func),


@solara.component_vue("../components/topic/topics_list.vue", vuetify=True)
def TopicsList(topics=["Topic 1", "Topic 2", "Topic 3"]):
    pass


@solara.component
def SectionTopics(current_selection: solara.Reactive[Section]):
    new_topic = solara.use_reactive("")
    topics = solara.use_reactive(["football", "cats", "dogs"])

    def add_topic():
        if new_topic.value:
            topics.value.append(new_topic.value)
            new_topic.value = ""

    section = current_selection.value

    with solara.Card():
        TopicInput(new_topic=new_topic, on_click_func=add_topic)
        TopicsList(topics=topics.value)


class State:
    # sections = solara.reactive([])
    # section = solara.reactive(None)

    @staticmethod
    def on_new(video, start: int, end: int, section_type: str):
        logger.debug(f"Adding new item: {start}, {end}, {section_type}")
        sm = SectionManager.from_video(video)
        sm.create_section(start=start, end=end, section_type=section_type)
        State.sections.value = sm.sections

    @staticmethod
    def on_delete(item: Section):
        logger.debug(f"Deleting item: {item}")
        new_items = list(State.sections.value)
        new_items.remove(item)
        SectionManager.delete_from_db(item)
        State.sections.value = new_items


@solara.component
def Page():

    def change_selected_section(data):
        logger.debug(f"Changing selected section to {data}")
        section.value = data
        # State.section.value = data

    MySidebar(router=solara.use_router())

    loading = solara.reactive(False)

    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    width, height = compute_graph_dimensions(video.duration)
    sections = Section.from_video(video)

    if sections == []:
        section = solara.reactive(None)
    else:
        section = solara.reactive(sections[0])

    with solara.Column(classes=["main-container"]):
        with solara.Row():
            with solara.Card():
                with solara.Card(title="Video Information", elevation=10):
                    VideoInfo(video)
                    AlbumInfo(video)

                with solara.Card(title="Section Control Panel", elevation=10):
                    SectionControlPanel(
                        video=video,
                        sections=sections,
                        current_selection=Ref(section),
                        on_new=State.on_new,
                        loading=loading,
                        on_delete=State.on_delete,
                    )
            with solara.Card(title="Jellyfin", elevation=10):
                JellyfinPanel(
                    current_video_youtube_id=video.youtube_id,
                    current_section=Ref(section),
                )

        with solara.Card():
            if loading.value:
                solara.SpinnerSolara(size="500px")
            elif len(sections) == 0:
                solara.Markdown("## No Sections Found. Please add some.")
            else:
                SectionGraphComponent(
                    sections,
                    current_selection=Ref(section),
                    on_click=lambda data: change_selected_section(data),
                    max_section_width=width,
                    max_section_height=height,
                )

                SectionTiming(
                    current_selection=Ref(section),
                    _video=video,
                )
                SectionTopics(
                    current_selection=Ref(section),
                )
