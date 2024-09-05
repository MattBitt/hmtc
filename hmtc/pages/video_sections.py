from typing import Callable, Dict
import solara
import solara.lab
from solara.lab.toestand import Ref
from loguru import logger
from hmtc.components.section.save_cancel import SectionSaveCancel
from hmtc.components.section.time_buttons import SectionTimeButtons
from hmtc.components.section.section_graph import SectionGraphComponent, format_sections
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.album.album_info import AlbumInfo
from hmtc.components.shared.jellyfin_panel import JellyfinPanel
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


def create_hms_dict(timestamp):
    # created on 9/4/24
    # used by video-sections page for input and
    # label (timestamp in milliseconds)
    return dict(
        hour=timestamp // 3600000,
        minute=(timestamp % 3600000) // 60,
        second=(timestamp % 3600000) % 60,
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
        solara.Button(f"Refresh", on_click=lambda: refreshing.set(True))
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
    num_sections = solara.use_reactive(len(sections.value))


    # text box for number of sections
    num_sections_input = solara.use_reactive(4)

    def delete_sections():
        loading.set(False)
        for section in sections.value:
            on_delete(section)
        loading.set(True)

    def clear_all_sections():
        loading.set(False)
        delete_sections()
        loading.set(True)

    def create_1_section():
        loading.set(False)
        sm = SectionManager.from_video(video)
        sm.create_section(start=0, end=video.duration, section_type=section_type.value)
        loading.set(True)

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
        loading.set(True)

    with solara.Column():

        if num_sections.value > 0:
            solara.Markdown(
                f"Section ID {current_section.value.id if current_section.value is not None else "asdf"} selected ({num_sections.value } found)"
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
):
    pass


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionTimeLine(
    timestamps=dict(
        whole_start=0,
        whole_end=2447,
        part_start=600,
        part_end=1200,
    )
):
    pass


@solara.component
def SectionTimeLabel(label, timestamp, editing):
    ts = create_hms_dict(timestamp)
    DigitLabel(
        label=label,
        timestamp=ts,
    )
    solara.Button(
        label="Edit",
        icon_name="mdi-pencil",
        on_click=lambda: editing.set(True),
        classes=["button"],
    )


@solara.component
def SectionTimeInput(section, label, timestamp, editing, correct_video, loading):
    ts = create_hms_dict(timestamp)

    def small_forward():
        if label=="Start Time":
            logger.debug(f"Small Forward: {section}")
            SectionManager.edit_section_start(section, increment=1)
        else:
            SectionManager.edit_section_end(section, increment=1)
        loading.set(True)
        
    
    def small_backward():
        logger.debug(f"Small Backward: {section}")
        if label=="Start Time":
            SectionManager.edit_section_start(section, increment=-1)
        else:
            SectionManager.edit_section_end(section, increment=-1)
        loading.set(True)


    DigitInput(
        label=label,
        timestamp=ts,
    )
    if correct_video:
        with solara.Row():
            solara.Button(
                "Play", on_click=lambda: logger.debug("Play"), classes=["button"]
            )
    SectionTimeButtons(
        small_forward=small_forward,
        small_backward=small_backward,
        large_forward=lambda: logger.debug(f"{label} Large Forward"),
        large_backward=lambda: logger.debug(f"{label} Large Backward"),
        tiny_forward=lambda: logger.debug(f"{label} Tiny Forward"),
        tiny_backward=lambda: logger.debug(f"{label} Tiny Backward"),
    )
    SectionSaveCancel(
        save=lambda: logger.debug("Save"),
        cancel=lambda: editing.set(False),
    )


@solara.component
def SectionTimeDisplay(video, section, loading, correct_video):

    editing_start = solara.use_reactive(False)
    editing_end = solara.use_reactive(False)

    timestamps = dict(
        whole_start=0,
        whole_end=video.duration,
        part_start=section.start,
        part_end=section.end,
    )

    SectionTimeLine(timestamps=timestamps)
    with solara.Row(justify="space-around"):
        if editing_start.value:
            SectionTimeInput(
                section=section,
                label="Start Time",
                timestamp=section.start,
                editing=editing_start,
                correct_video=correct_video,
                loading=loading,
            )
        else:
            SectionTimeLabel(
                label="Start Time",
                timestamp=section.start,
                editing=editing_start,
            )

        if editing_end.value:
            SectionTimeInput(
                section=section,
                label="End Time",
                timestamp=section.end,
                editing=editing_end,
                correct_video=correct_video,
                loading=loading,
            )
        else:
            SectionTimeLabel(
                label="End Time",
                timestamp=section.end,
                editing=editing_end,
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
def SectionTopics(section: solara.Reactive[Section]):
    new_topic = solara.use_reactive("")
    topics = solara.use_reactive(["football", "cats", "dogs"])

    def add_topic():
        if new_topic.value:
            topics.value.append(new_topic.value)
            new_topic.value = ""

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

    @staticmethod
    def on_delete(item: Section):
        logger.debug(f"Deleting item: {item}")
        SectionManager.delete_from_db(item)


@solara.component
def Page():

    MySidebar(router=solara.use_router())

    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    width, height = compute_graph_dimensions(video.duration)

    sections = solara.use_reactive(Section.from_video(video))
    section = solara.reactive(None)

    model = solara.use_reactive(0)
    connected = solara.use_reactive(False)
    correct_video = solara.use_reactive(False)

    if len(sections.value) > 0:
        section.set(sections.value[0])

    loading = solara.reactive(False)

    def change_selected_section(data):
        logger.debug(f"Changing selected section to one with end time:{data}")
        sect = Section.get_by_end(video_id=video.id, end=data)
        section.set(sect)
        model.value = sections.value.index(sect)
        logger.debug(f"Setting Section as active: {sect}")

    if loading.value:
        with solara.Card():
            solara.SpinnerSolara(size="500px")
    else:
        with solara.Column(classes=["main-container"]):
            with solara.Row():
                with solara.Column():
                    with solara.Card(
                        title="Video Information",
                    ):
                        VideoInfo(video, refreshing=loading)
                        AlbumInfo(video)

                    with solara.Card(title="Section Control Panel"):
                        SectionControlPanel(
                            video=video,
                            sections=sections,
                            current_section=section,
                            on_new=State.on_new,
                            loading=loading,
                            on_delete=State.on_delete,
                        )
                with solara.Card(title="Jellyfin"):
                    JellyfinPanel(
                        current_video_youtube_id=video.youtube_id,
                        current_section=section,
                        status=dict(connected=connected, correct_video=correct_video),
                    )

            with solara.Column():
                if len(sections.value) == 0:
                    solara.Markdown("## No Sections Found. Please add some.")
                else:
                    formatted_sections = format_sections(sections.value)
                    with solara.Card():
                        SectionGraphComponent(
                        formatted_sections=formatted_sections,
                        on_click=lambda data: change_selected_section(data),
                        max_section_width=width,
                        max_section_height=height,
                    )
                    with solara.Card():
                        with Carousel(model=model.value):
                            for sect in sections.value:

                                with solara.Column():
                                    SectionTimeDisplay(
                                    video=video,
                                    section=sect,
                                    loading=loading,
                                    correct_video=correct_video.value,
                                )
                                    SectionTopics(
                                    section=sect,
                                )
