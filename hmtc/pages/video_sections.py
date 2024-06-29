from typing import Callable

import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.section.section_graph import SectionGraphComponent
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Section as SectionTable
from hmtc.models import Video
from hmtc.mods.section import Section, SectionManager
from hmtc.mods.album import Album

title = "Section Editor"


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


# @solara.component
# def Sidebar():
#     with solara.Sidebar():
#         solara.Markdown("Sidebar")
#         with solara.Column(style={"flex-direction": "column", "align-items": "left"}):
#             solara.Button("Videos", href="/videos", outlined=True)
#             solara.Button("Playlists", href="/playlists", outlined=True)
#             solara.Button("Settings", href="/settings", outlined=True, color="red")


@solara.component_vue("../components/section/section_item.vue", vuetify=True)
def SectionItem(
    event_button_click: Callable[[dict], None],
    event_set_start_time: Callable[[str], None],
    event_set_end_time: Callable[[str], None],
    event_set_section_type: Callable[[str], None],
    event_load_next_section: Callable[[dict], None],
    event_load_previous_section: Callable[[dict], None],
    section=dict(id=15, start="00:00:00", end="23:59:59"),
):
    pass


@solara.component
def SectionCarousel(
    slides,
    selected_section: solara.Reactive[Section],
    next_section: Callable[[dict], None],
    previous_section: Callable[[dict], None],
):
    start_time = solara.use_reactive(selected_section.value.start)
    end_time = solara.use_reactive(selected_section.value.end)
    section_type = solara.use_reactive(selected_section.value.section_type)

    def complicated_function(*args):
        logger.error(f"Args = {args}")
        return args[0]

    def set_section_type(*args):
        logger.error(f"Args = {args}")
        return args[0]

    def load_next_section(*args):
        logger.debug("Loading Next Section:")
        next_section(args[0])

    def load_previous_section(*args):
        logger.debug("Loading Previous Section:")
        logger.error(f"Args = {args}")
        return args[0]

    with solara.Column(style={"min-width": "600px"}):
        # solara.Markdown(f"Current Selection: {selected_section.value}")
        SectionItem(
            section=dict(
                id=selected_section.value.id,
                start=start_time.value,
                end=end_time.value,
                is_first=False,
                is_last=False,
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
            event_load_next_section=lambda data: load_next_section(data),
            event_load_previous_section=lambda data: load_previous_section(data),
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

    def split_evenly():
        loading.value = True
        num_sections.value = video.duration // 60
        split()
        loading.value = False

    with solara.Column():
        solara.Markdown("#### Section Control Panel")
        with solara.Column(align="center"):
            solara.Button("Single Section", on_click=split_into_1, classes=["button"])
            solara.Button("Split Evenly", on_click=split_evenly, classes=["button"])
            solara.Button(
                "Clear All Sections", on_click=clear_sections, classes=["button"]
            )


@solara.component
def AlbumInfo(video, album):
    def delete_album():
        album.value.delete_album()
        album.set(None)

    def create_album():
        Album.create_for_video(video)
        album.set(Album.grab_for_video(video.id))

    def update_album():
        logger.debug("Updating Album")
        Album.update_album(title=album.value.title, video_id=video.id)

    has_album = album.value is not None
    if has_album:
        solara.InputText(
            label="Album Title",
            value=album.value.title,
            on_value=lambda x: album.set(Album(title=x, video_id=video.id, tracks=[])),
        )
        solara.Button(
            label="Save Album",
            on_click=update_album,
        )
        solara.Button(
            f"Delete Album",
            on_click=delete_album,
        )
    else:
        solara.Button(
            f"Create Album",
            on_click=create_album,
            disabled=has_album,
        )


@solara.component
def VideoInfo(video):
    h, m, s = video.duration // 3600, (video.duration % 3600) // 60, video.duration % 60
    duration_string = f"{h:02d}:{m:02d}:{s:02d}"

    with solara.Column():
        solara.Markdown(f"### {video.title}")

        with solara.Row(justify="space-between"):
            solara.Markdown(f"#### Duration: **{duration_string}**")
            with solara.Column():
                solara.Markdown("Section ID")

        solara.Button(
            icon_name="mdi-youtube",
            icon=True,
            href=video.url,
        )


### Don't know if this is true, but should be when finished
### reusable above this line
### below this line is the page definition


class State:
    loading = solara.reactive(False)
    selected_section = solara.reactive(None)

    @staticmethod
    def load_sections():
        video_id = parse_url_args()

        State.video = Video.get_by_id(video_id)
        if State.video.duration == 0:
            solara.Error("Video has no duration. Please Refresh from youtube.")
            return

        sm = SectionManager.from_video(State.video)
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
        State.width, State.height = compute_graph_dimensions(State.video.duration)

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

    @staticmethod
    def on_click_graph(*args):
        logger.debug(f"on_click called with data: {args}")
        id = args[0]["id"]
        logger.debug(f"ID: {id}")
        sect = SectionTable.select().where(SectionTable.id == id).get()
        if sect:
            State.select_section(sect)
        else:
            logger.debug("No section found🧬🧬🧬")

    @staticmethod
    def previous_section(*args):
        logger.debug(f"Previous Section Called with: {args}")
        if State.selected_section.value is None:
            return

        idx = State.sections.value.index(State.selected_section.value)
        if idx == 0:
            return
        State.select_section(State.sections.value[idx - 1])

    @staticmethod
    def next_section(*args):
        logger.debug(f"Next Section Called with: {args}")
        if State.selected_section.value is None:
            return
        idx = State.sections.value.index(State.selected_section.value)
        if idx == len(State.sections.value) - 1:
            return
        State.select_section(State.sections.value[idx + 1])


@solara.component
def Page():
    State.load_sections()

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
    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        with solara.Columns(6, 6):
            VideoInfo(State.video)
            album = solara.use_reactive(Album.grab_for_video(State.video.id))
            with solara.Card():
                AlbumInfo(State.video, album)

            SectionControlPanel(
                video=State.video,
                on_new=State.on_new,
                loading=State.loading,
                on_delete=State.on_delete,
            )

        if State.loading.value:
            with solara.Column():
                solara.SpinnerSolara(size="100px")
        else:
            if State.video.sections.count() == 0:
                solara.Markdown("## No Sections Found. Please add some.")
                return

            SectionGraphComponent(
                State.video.sections,
                current_selection=Ref(State.selected_section),
                on_click=State.on_click_graph,
                max_section_width=State.width,
                max_section_height=State.height,
            )

            SectionCarousel(
                slides=carousel_sections,
                selected_section=Ref(State.selected_section),
                next_section=State.next_section,
                previous_section=State.previous_section,
            )
