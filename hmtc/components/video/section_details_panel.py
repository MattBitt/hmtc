from pathlib import Path

import PIL
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.config import init_config
from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopic as SectionTopicsModel,
)
from hmtc.models import (
    Series as SeriesModel,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import (
    Track as TrackModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.models import (
    YoutubeSeries as YoutubeSeriesModel,
)
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.time_functions import seconds_to_hms, time_ago_string

reload = solara.reactive(False)


@solara.component_vue("SectionSelector.vue", vuetify=True)
def SectionSelector(
    sectionItems,
    video_duration,
    event_add_item,
    event_remove_item,
    event_delete_section,
    event_update_times,
    event_update_section_from_jellyfin,
    event_create_section_from_jellyfin,
    event_create_track,
    event_remove_track,
    event_refresh_panel,
    event_create_audio_file,
    event_delete_audio_file,
    event_create_lyrics_file,
    event_delete_lyrics_file,
):
    pass


def delete_section(*args, **kwargs):
    logger.debug(f"Deleting Section: {args}")
    # SectionItem.delete_id(args[0]["section_id"])
    logger.success(f"Deleted Section {args[0]['section_id']} successfully")


def update_section_times(*args):
    logger.debug(f"Updating Section Times: {args}")
    try:
        section = SectionModel.get_by_id(args[0]["item_id"])
    except Exception as e:
        logger.error(e)
        return
    if "start" in args[0].keys():
        section.start = args[0]["start"]
    if "end" in args[0].keys():
        section.end = args[0]["end"]
    section.save()


def create_track(*args):
    # .create(track_data=args[0], album_id=video.album_id)
    pass


def remove_track(section_id):
    section = SectionModel.get_by_id(section_id)
    try:
        track = TrackModel.select().where(TrackModel.id == section.track_id).get()
        track.delete_instance(recursive=True)
    except Exception as e:
        logger.error(e)
        logger.error(f"Track not found for section {section_id}")
        return


def add_topic(*args):
    section_id = args[0]["item_id"]
    topic = args[0]["topic"]
    if section_id is None or topic is None:
        logger.error("Section ID or Topic is None")
        return
    topic, created = TopicModel.get_or_create(text=topic)
    if created:
        logger.debug(f"Created topic {topic.text}")
    _order = (
        SectionTopicsModel.select()
        .where(SectionTopicsModel.section_id == section_id)
        .count()
    )
    SectionTopicsModel.create(
        section_id=section_id, topic_id=topic.id, order=_order + 1
    )
    logger.debug(f"adding topic {topic} to section {section_id}")
    reload.set(True)


def remove_topic(*args):
    section_id = args[0]["item_id"]
    topic = args[0]["topic"]
    logger.debug(f"remove_topic: {topic} from seciton {section_id}")

    t = TopicModel.select().where(TopicModel.text == topic).get_or_none()
    if t is None:
        logger.error(f"Topic {args[0]} not found")
        return

    SectionTopicsModel.delete().where(
        (SectionTopicsModel.section_id == section_id)
        & (SectionTopicsModel.topic_id == t.id)
    ).execute()

    topic_still_needed = SectionTopicsModel.get_or_none(
        SectionTopicsModel.topic_id == t.id
    )
    if topic_still_needed is None:
        logger.debug(f"Topic no longer needed {t.text} ({t.id}). Removing.")
        t.delete_instance()

    logger.error(f"Removed topic {t.text} ({t.id}) from section {section_id}")
    reload.set(True)


def create_audio_file(*args):
    logger.debug(f"Creating audio file {args}")
    try:
        tm = TrackModel.get_by_id(args[0]["track_id"])
        # track = TrackItem.from_model(tm)
        # track.create_audio_file(video=video)
    except Exception as e:
        logger.error(e)
        return

    reload.set(True)


def delete_audio_file(*args):
    logger.error(f"Deleting audio file {args}")
    try:
        track = TrackModel.select().where(TrackModel.id == args[0]).get()
        # FileManager.delete_track_file(track, "audio")
    except Exception as e:
        logger.error(e)
        return
    reload.set(True)


def create_lyrics_file(*args):
    logger.debug(f"Creating audio file {args}")
    try:
        tm = TrackModel.get_by_id(args[0]["track_id"])
        # track = TrackItem.from_model(tm)
        # track.create_lyrics_file(video=video)
    except Exception as e:
        logger.error(e)
        return
    reload.set(True)


def delete_lyrics_file(*args):
    logger.error(f"Deleting lyrics file {args}")
    try:
        track = TrackModel.select().where(TrackModel.id == args[0]).get()
        # FileManager.delete_track_file(track, "lyrics")
    except Exception as e:
        logger.error(e)
        return
    reload.set(True)


@solara.component
def SectionsDetailsPanel(video, sections):

    _sections = [s.serialize() for s in sections]

    if _sections != []:
        SectionSelector(
            sectionItems=_sections,
            video_duration=video.instance.duration,
            event_add_item=add_topic,
            event_remove_item=remove_topic,
            event_delete_section=delete_section,
            event_update_times=update_section_times,
            event_create_track=create_track,
            event_remove_track=remove_track,
            event_refresh_panel=lambda x: reload.set(True),
            event_create_audio_file=lambda x: create_audio_file(x),
            event_delete_audio_file=lambda x: delete_audio_file(x),
            event_create_lyrics_file=lambda x: create_lyrics_file(x),
            event_delete_lyrics_file=lambda x: delete_lyrics_file(x),
        )
