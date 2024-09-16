from typing import cast, Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video, Section, Series, YoutubeSeries
from hmtc.mods.section import SectionManager
from hmtc.schemas.video import VideoItem
import peewee
import pandas as pd
from loguru import logger
from hmtc.components.shared.jellyfin_panel import JellyfinPanel, JellyfinSessionInfo
from hmtc.utils.jf import jellyfin_loop_2sec, jellyfin_sessions, get_current_session, grab_now_playing

force_update_counter = solara.reactive(0)


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        # solara.Markdown("No Video Selected")
        # raise ValueError("No video selected")
        # use this to view all sections
        return None

    return router.parts[level:][0]


@solara.component_vue("../components/section/section_table.vue", vuetify=True)
def SectionTable(
    items: list = [],
    current_position: int = 0,
    event_save_section=None,
    event_delete_section: Callable = None,
    event_loop_jellyfin: Callable = None,
):
    pass





def delete_section(section):
    logger.debug(f"Deleting Item received from Vue: {section["id"]}")
    try:
        section = Section.get_by_id(section["id"])
        section.delete_instance()
    except Exception as e:
        logger.error(f"Error deleting section: {section["id"]}. Error: {e}")


def save_section(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        section = Section.get_by_id(item["id"])
    except Exception as e:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Section ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        Section.create(**edited_item)
        return

    section.section_type = edited_item["section_type"]
    section.start = edited_item["start"]
    section.end = edited_item["end"]
    section.save()
    force_update_counter.set(force_update_counter.value + 1)


def create_single_section(video_id, duration, section_type="INITIAL"):
    sm = SectionManager(video_id=video_id.id, duration=duration)
    sm.create_section(start=0, end=duration, section_type=section_type.value)


@solara.component
def SectionControlPanel(
    video,
):
    MIN_SECTION_LENGTH = 10
    MAX_SECTION_LENGTH = 99999

    # i took this component from the video_sections.py file
    # on 9/13/24. I think that whole page will be deprecated eventually
    # but want to simplify this
    section_type = solara.use_reactive("intro")
    sm = SectionManager.from_video(video)
    # existing sections
    num_sections = solara.use_reactive(len(sm.sections))

    # text box for number of sections
    num_sections_input = solara.use_reactive(4)

    def clear_all_sections():
        for section in sm.sections:
            logger.error(f"Deleting section {section}")
            delete_section(section.model_to_dict())
        
        force_update_counter.set(force_update_counter.value + 1)
    
    def create_1_section():

        sm = SectionManager.from_video(video)
        sm.create_section(start=0, end=video.duration, section_type=section_type.value)
        force_update_counter.set(force_update_counter.value + 1)

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
        sm = SectionManager.from_video(video)
        for i in range(num_new_sections):
            logger.error("Creating section")
            sm.create_section(start=i * (video.duration / num_new_sections), end=(i + 1) * (video.duration / num_new_sections), section_type=section_type.value)
        
        force_update_counter.set(force_update_counter.value + 1)

    with solara.Column():

        if num_sections.value > 0:
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
def Page():

    MySidebar(solara.use_router())

    video_id = parse_url_args()
    if video_id is not None:
        video = VideoItem.get_details_for_video(video_id)
        base_query = Section.select().where(Section.video_id == video_id)
    else:
        video = None
        base_query = Section.select()

    current_session = get_current_session()
    
    if current_session is None:
        logger.error(f"No Jellyfin session found")
        user_session = solara.reactive(None)
    else:
        user_session = solara.use_reactive(current_session)

    def loop_jellyfin(timestamp):
        logger.debug(f"Looping Jellyfin at timestamp: {timestamp}")
        # need to rework this function to take a session maybe?
        jellyfin_loop_2sec(session_id=user_session.value['Id'], position=timestamp)

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        if video is not None:
            solara.Markdown(f"Video: {video.title}")
            SectionControlPanel(video=video)
            if user_session.value is not None:
                now_playing = grab_now_playing(session=user_session.value)
                JellyfinPanel(current_video_youtube_id=video.youtube_id, current_section=None, status=None, jf_session=user_session)
        SectionTable(
            items=items,
            current_position=now_playing['position']*1000 if user_session.value is not None else 0,
            event_save_section=save_section,
            event_delete_section=delete_section,
            event_loop_jellyfin = loop_jellyfin,

        )
