import re
from pathlib import Path

import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import File as FileModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_current_user_timestamp,
    get_currently_playing,
    get_user_favorites,
    get_user_session,
    jf_pause,
    jf_play,
    jf_playpause,
    jf_stop,
)


@solara.component_vue("../components/track/LyricsScroller.vue", vuetify=True)
def LyricsScroller(lyrics, currentTimestamp, event_update):
    pass


@solara.component
def Lyrics(lyrics, currentTimestamp):
    timestamp = solara.use_reactive(0)

    def update_timestamp(*args):
        # logger.error(f"update_timestamp {timestamp.value}")
        session_timestamp = get_current_user_timestamp()
        if session_timestamp is not None:
            timestamp.set(session_timestamp)
        else:
            pass
            # logger.debug("No client session found")
            # should probably turn off updating or something
            # here?

    solara.Markdown("### Lyrics")
    LyricsScroller(
        lyrics=lyrics,
        currentTimestamp=timestamp.value,
        event_update=update_timestamp,
    )


def parse_lrc_line(line):
    match = re.match(r"\[(\d+):(\d+):(\d+\.\d+)\](.*)", line)
    if match:
        hours, minutes, seconds, text = match.groups()
        timestamp = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return {"text": text.strip(), "timestamp": timestamp}
    logger.error(f"Could not parse line: {line}")
    return None


def read_lyrics(path):
    with open(path, "r") as f:
        lyrics = f.readlines()
        raw_text = [line.strip() for line in lyrics]
        lyrics = [parse_lrc_line(line) for line in raw_text if parse_lrc_line(line)]
    return lyrics


def find_jellyfin_id_in_db(jf_id):
    vid = VideoModel.select().where(VideoModel.jellyfin_id == jf_id).get_or_none()
    if vid is not None:
        return "video", vid
    track = TrackModel.select().where(TrackModel.jellyfin_id == jf_id).get_or_none()
    if track is not None:
        return "track", track
    logger.error(f"Could not find {jf_id} in database")
    return None, None


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    jf_id = get_currently_playing()

    if jf_id is None:
        solara.Markdown("### No Jellyfin id found/Not playing anything")
        return
    session = get_user_session()
    solara.Markdown(f"### Currently Playing id: {jf_id}")
    library, item = find_jellyfin_id_in_db(jf_id)
    if library is None:
        solara.Markdown(f"### Could not find library {jf_id} in database")
        return
    if item is None:
        solara.Markdown(f"### Could not find {jf_id} in database")
        return
    solara.Markdown(f"### Found in db: {library} {item.title}")
    if library == "track":
        with solara.Row(justify="end"):
            solara.Button(
                icon_name="mdi-heart",
                color="primary",
                on_click=lambda: logger.debug("favorite"),
            )
            solara.Button(
                icon_name="mdi-flag",
                color="primary",
                on_click=lambda: logger.debug("flagged"),
            )
        timestamp = solara.use_reactive(0)
        file = (
            FileModel.select()
            .where((FileModel.file_type == "lyrics") & (FileModel.track_id == item.id))
            .get()
        )
        logger.debug(f"File has lyrics: {file.filename}")
        lyrics = read_lyrics(Path(file.path) / file.filename)
        if lyrics:
            Lyrics(lyrics=lyrics, currentTimestamp=timestamp)
        else:
            solara.Markdown("### No lyrics found. Add some to see them")

        with solara.Row(justify="center"):
            solara.Button(
                "Play/Pause",
                color="primary",
                on_click=jf_playpause,
            )
            solara.Button(
                "Stop",
                color="primary",
                on_click=jf_stop,
            )

    elif library == "video":
        video = VideoModel.select().where(VideoModel.jellyfin_id == jf_id).get()
        solara.Markdown("### Video")
        solara.Markdown(f"#### {video.title}")
