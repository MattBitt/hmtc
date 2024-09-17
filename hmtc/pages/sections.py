import time
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
from hmtc.utils.jf import (
    jellyfin_loop_2sec,
    jellyfin_sessions,
    get_current_session,
    grab_now_playing,
)
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from pathlib import Path
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
    is_connected: bool = False,
    has_active_user_session: bool = False,
    play_status: bool = False,
    current_position: int = 0,
    event_save_section: Callable = None,
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
def NewJellyfinPanel(jf, video):
   
    
    def local_load_item():
        if video.jellyfin_id is None:
            logger.error("No Jellyfin ID for this video")
            return

        jf.load_media_item(jellyfin_id=video.jellyfin_id)

    if jf.play_status == "stopped":
        # no media item loaded
        is_video_id_playing_in_jellyfin = False
    else:
        is_video_id_playing_in_jellyfin = (jf.media_item["Id"] == video.jellyfin_id)
    
    pth = Path('./hmtc/assets/icons/jellyfin.1024x1023.png')
    
    with solara.Card():
        solara.Image(pth, width="80px")
        solara.Markdown(f"Jellyfin Connected: {jf.is_connected}")
        if jf.is_connected:
            if jf.has_active_user_session:
                solara.Markdown(f"Jellyfin Session ID: {jf.session_id}")
                solara.Markdown(f"Jellyfin User: {jf.user}")
            

                with solara.Row():
                    if is_video_id_playing_in_jellyfin:
                        solara.Markdown(f"Title: {jf.media_item['Name']}")
                        solara.Markdown(f"Position: {jf.position}")
                        solara.Button(f"Play/Pause Jellyfin", on_click=jf.play_pause, classes=["button"])
                        solara.Button(f"Pause Jellyfin", on_click=jf.pause, classes=["button"])
                        solara.Button(f"Stop Jellyfin", on_click=jf.stop, classes=["button"])
                solara.Button(f"Load 'This' Video", on_click=local_load_item, disabled=is_video_id_playing_in_jellyfin , classes=["button"])
            else:
                logger.debug("No active Jellyfin session found")
                solara.Markdown("No active Jellyfin session found")
        else:
            logger.debug("Jellyfin not connected")
            solara.Markdown("Jellyfin not connected")


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
            sm.create_section(
                start=i * (video.duration / num_new_sections),
                end=(i + 1) * (video.duration / num_new_sections),
                section_type=section_type.value,
            )

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
        # the plan for this would be a sections table (regardless of video)
        # didn't seem to work, but didn't mess with it much
        video = None
        base_query = Section.select()

    jf = MyJellyfinClient().connect()

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        if video is not None:
            solara.Markdown(f"Video: {video.title}")
            SectionControlPanel(video=video)
        with solara.Card():
            NewJellyfinPanel(jf, video=video)

        
        SectionTable(
            items=items,
            is_connected=jf.is_connected,
            has_active_user_session=jf.has_active_user_session,
            play_status=jf.play_status,
            current_position=jf.position,
            event_save_section=save_section,
            event_delete_section=delete_section,
            event_loop_jellyfin=lambda timestamp: logger.debug(
                f"Looping Jellyfin at timestamp: {timestamp}"
            ),
        )
