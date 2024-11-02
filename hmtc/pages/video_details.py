from pathlib import Path

import PIL
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.vue_registry import register_vue_components
from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.models import (
    File as FileModel,
)
from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopics as SectionTopicsModel,
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
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.section import SectionManager
from hmtc.schemas.track import TrackItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.utils.time_functions import seconds_to_hms, time_ago_string
from hmtc.utils.youtube_functions import download_video_file

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"
MIN_SECTION_LENGTH = 60
MAX_SECTION_LENGTH = 1200
AVERAGE_SECTION_LENGTH = 180
IMG_WIDTH = "300px"

loading = solara.reactive(False)
reactive_sections = solara.reactive([])


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        # 10/26/24 - not sure what this is doing
        return None

    return router.parts[level:][0]


# 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
# Section - Admin Panel


def delete_all_sections(*args):
    for section in reactive_sections.value:
        logger.debug(f"Deleting Section: {section}")
        delete_section_from_db(section.id)

    reactive_sections.set([])


def create_section(video, start, end, section_type="instrumental"):
    sm = SectionManager.from_video(video)
    new_sect_id = sm.create_section(start=start, end=end, section_type="instrumental")
    new_sect = SectionModel.get_by_id(new_sect_id)
    reactive_sections.set(reactive_sections.value + [new_sect])


def delete_section_from_db(section_id):
    logger.debug(f"Deleting Section: {section_id}")
    SectionTopicsModel.delete().where(
        SectionTopicsModel.section_id == section_id
    ).execute()

    SectionModel.delete_by_id(section_id)


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


def update_section_from_jellyfin(section_id, start_or_end, video, reactive_sections):
    logger.error("deprecated 10/26/24")


@solara.component_vue("../components/section/SectionControlPanel.vue", vuetify=True)
def SectionControlPanel(
    video,
    jellyfin_status,
    event_delete_all_sections,
    event_create_section,
):
    pass


@solara.component
def SectionsPanel(
    video,
    reactive_sections,
    update_section_from_jellyfin,
):
    reload = solara.use_reactive(False)
    # not sure why this is a tuple...
    section_dicts = (
        solara.use_reactive(
            [SectionManager.get_section_details(s.id) for s in reactive_sections.value]
        ),
    )
    section_type = solara.use_reactive("instrumental")

    if len(reactive_sections.value) > 0:
        tab_items = section_dicts[0].value
    else:
        tab_items = []

    def delete_section(*args, **kwargs):
        logger.debug(f"Deleting Section: {args}")
        delete_section_from_db(args[0]["section_id"])
        reactive_sections.set(
            [s for s in reactive_sections.value if s.id != args[0]["section_id"]]
        )
        reload.set(True)

    def create_section_at_jellyfin_position(*args):

        jf = MyJellyfinClient()
        jf.connect()
        status = jf.get_playing_status_from_jellyfin()
        try:
            pos = status["position"]

        except Exception as e:
            logger.error(f"Error getting position from Jellyfin: {e}")
            return

        try:
            start_or_end = args[0]["start_or_end"]
        except Exception as e:
            logger.error(e)
            return

        sm = SectionManager.from_video(video)
        if start_or_end == "start":
            new_start = pos
            new_end = (
                (pos + AVERAGE_SECTION_LENGTH)
                if (pos + AVERAGE_SECTION_LENGTH) < video.duration
                else video.duration
            )
        else:
            new_start = pos - AVERAGE_SECTION_LENGTH
            new_end = pos

        new_sect_id = sm.create_section(
            start=new_start,
            end=new_end,
            section_type=section_type.value,
        )
        new_sect = SectionModel.get_by_id(new_sect_id)
        reactive_sections.set(reactive_sections.value + [new_sect])
        reload.set(True)

    def create_track(args):
        try:
            album = AlbumModel.get_by_id(video.album_id)
        except Exception as e:
            logger.error(e)
            return
        album_item = AlbumItem.from_model(album)
        section_id = args.pop("section_id")
        section = SectionModel.get_by_id(section_id)

        track = album_item.create_track(**args)
        section.track = track
        section.save()
        reload.set(True)

    def remove_track(section_id):
        section = SectionModel.get_by_id(section_id)
        try:
            track = TrackModel.select().where(TrackModel.id == section.track_id).get()
            track.delete_instance(recursive=True)
        except Exception as e:
            logger.error(e)
            logger.error(f"Track not found for section {section_id}")
            return
        reload.set(True)

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
        # this is just the beginning
        # still need to update the id3 properties
        # and assign a poster image
        logger.debug(f"Creating audio file {args}")
        try:
            tm = TrackModel.get_by_id(args[0]["track_id"])
        except Exception as e:
            logger.error(e)
            return
        track = TrackItem.from_model(tm)
        try:
            input_file = (
                FileModel.select()
                .where(
                    (FileModel.video_id == video.id) & (FileModel.file_type == "audio")
                )
                .get()
            )
        except:
            logger.error(f"No input file found for")
            return
        input_file_path = Path(input_file.path) / input_file.filename
        image_file_path = FileManager.get_file_for_video(video, "poster")
        im_file = Path(image_file_path.path) / image_file_path.filename
        track_path = track.write_audio_file(
            audio_file=input_file_path, image_file=im_file
        )
        new_file = FileManager.add_path_to_track(
            path=track_path, track=track, video=video
        )
        logger.debug(f"Created audio file {new_file}")

        reload.set(True)

    def delete_audio_file(*args):
        logger.error(f"Deleting audio file {args}")
        try:
            track = TrackModel.select().where(TrackModel.id == args[0]).get()
            FileManager.delete_track_file(track, "audio")
        except Exception as e:
            logger.error(e)
            return

    def create_lyrics_file(*args):
        logger.debug(f"Creating lyrics file {args}")
        # args is a dict with 'track_id' as the key
        try:
            input_file = (
                FileModel.select()
                .where(
                    (FileModel.video_id == video.id)
                    & (FileModel.file_type == "subtitle")
                )
                .get()
            )
        except:
            logger.error(f"No input file found for")
            return
        input_file_path = Path(input_file.path) / input_file.filename
        track_item = TrackItem.from_model(TrackModel.get_by_id(args[0]["track_id"]))
        lyrics_path = track_item.write_lyrics_file(input_file=input_file_path)

        new_file = FileManager.add_path_to_track(
            path=lyrics_path, track=track_item, video=video
        )
        logger.debug(f"Created lyrics file {new_file}")

        reload.set(True)

    def delete_lyrics_file(*args):
        logger.error(f"Deleting lyrics file {args}")
        try:
            track = TrackModel.select().where(TrackModel.id == args[0]).get()
            FileManager.delete_track_file(track, "lyrics")
        except Exception as e:
            logger.error(e)
            return

    if not reload.value:
        if tab_items != []:
            SectionSelector(
                sectionItems=tab_items,
                video_duration=video.duration,
                event_add_item=add_topic,
                event_remove_item=remove_topic,
                event_delete_section=delete_section,
                event_update_times=update_section_times,
                event_update_section_from_jellyfin=update_section_from_jellyfin,
                event_create_section_from_jellyfin=create_section_at_jellyfin_position,
                event_create_track=create_track,
                event_remove_track=remove_track,
                event_refresh_panel=lambda x: reload.set(True),
                event_create_audio_file=lambda x: create_audio_file(x),
                event_delete_audio_file=lambda x: delete_audio_file(x),
                event_create_lyrics_file=lambda x: create_lyrics_file(x),
                event_delete_lyrics_file=lambda x: delete_lyrics_file(x),
            )
    else:
        solara.Markdown(f"## Reloading Panel")
        reload.set(False)


# started refactor on 10/25/2024
# components below have been looked at and are working


@solara.component_vue("../components/video/SectionSelector.vue", vuetify=True)
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


# 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
# Video - File controls


def get_video_files(video_id, youtube_id):
    db_files = (
        FileModel.select()
        .where(FileModel.video_id == video_id)
        .order_by(FileModel.filename)
    )
    if len(db_files) == 0:
        logger.error(f"No files found for video {video_id}")
        if youtube_id is None:
            logger.error("No youtube id found")
            return [], []
        folder_to_search = STORAGE / youtube_id
    else:
        folder_to_search = Path(db_files[0].path)

    folder_files = [x for x in list(folder_to_search.rglob("*")) if x.is_file()]
    if folder_files != []:
        folder_files = sorted(folder_files, key=lambda x: x.name)
    return db_files, folder_files


def remove_existing_files(video_id, youtube_id, file_types):
    db_files, _ = get_video_files(video_id, youtube_id)
    existing_vid_files = [x for x in db_files if (x.file_type in file_types)]
    for vid_file in existing_vid_files:
        # the below will delete files found in the database from the filesystem
        try:
            vid_file.delete_instance()
            file_to_delete = Path(vid_file.path) / vid_file.filename
            file_to_delete.unlink()

        except Exception as e:
            logger.error(f"Error deleting file {e}")

    # the below will delete files found in the video's folder
    # regardless if they are in the db or not

    extensions = []
    if "video" in file_types:
        extensions += [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"]
    if "audio" in file_types:
        extensions += [".mp3", ".m4a", ".flac", ".wav", ".ogg"]
    if "info" in file_types:
        extensions += [".info.json", ".json"]
    if "subtitle" in file_types:
        extensions += [".srt", ".en.vtt"]
    if "poster" in file_types:
        extensions += [".jpg", ".jpeg", ".png", ".webp"]

    _, folder_files = get_video_files(video_id, youtube_id)
    for file in folder_files:
        if file.suffix in extensions:
            logger.debug(f"Found video file: {file}. Deleting")
            file.unlink()


@solara.component_vue("../components/file/file_type_checkboxes.vue", vuetify=True)
def FileTypeCheckboxes(
    db_files,
    folder_files,
    has_audio: bool = False,
    has_video: bool = False,
    has_subtitle: bool = False,
    has_info: bool = False,
    has_poster: bool = False,
    has_album_nfo: bool = False,
    event_download_video: callable = None,
    event_download_info: callable = None,
    event_create_album_nfo: callable = None,
):
    pass


@solara.component
def FilesPanel(video):
    files = FileModel.select().where(FileModel.video_id == video.id)
    loading = solara.use_reactive(False)
    status_message = solara.use_reactive("")

    def download_info(*args):
        loading.set(True)
        remove_existing_files(
            video.id, video.youtube_id, ["info", "subtitle", "poster"]
        )
        VideoItem.refresh_youtube_info(video.id)
        create_album_nfo()
        loading.set(False)

    def download_video(*args):
        loading.set(True)
        logger.info(f"Downloading video: {video.title}")
        remove_existing_files(video.id, video.youtube_id, ["video", "audio"])
        info, files = download_video_file(video.youtube_id, WORKING, progress_hook=None)

        vid = VideoModel.select().where(VideoModel.id == video.id).get()
        for file in files:
            logger.debug(f"Processing files in download_video of the list item {file}")
            FileManager.add_path_to_video(file, vid)
            # this is where i need to add the jellyfin id to the database,
            # but, i need to make sure that the video is in jellyfin first
        loading.set(False)

    def create_album_nfo(*args):
        # need to check if file exists and remove it
        # and if its alread in the db, remove it
        loading.set(True)
        remove_existing_files(video.id, video.youtube_id, ["album_nfo"])

        new_file = VideoItem.create_xml_for_jellyfin(video.id)
        FileManager.add_path_to_video(new_file, video)
        loading.set(False)

    db_files, folder_files = get_video_files(video.id, video.youtube_id)
    ff_serialized = [dict(name=x.name) for x in folder_files]
    file_types_found = [x.file_type for x in files]
    if loading.value:
        with solara.Row(justify="center"):
            MySpinner()
            solara.Text(f"{status_message.value}")
    else:

        FileTypeCheckboxes(
            db_files=[x.model_to_dict() for x in db_files],
            folder_files=ff_serialized,
            has_audio="audio" in file_types_found,
            has_video="video" in file_types_found,
            has_info="info" in file_types_found,
            has_subtitle="subtitle" in file_types_found,
            has_poster="poster" in file_types_found,
            has_album_nfo="album_nfo" in file_types_found,
            event_download_video=download_video,
            event_create_album_nfo=create_album_nfo,
            event_download_info=download_info,
        )


# 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
# Video Info


@solara.component
def VideoInfoPanelLeft(video):

    poster = FileManager.get_file_for_video(video, "poster")
    image = PIL.Image.open(Path(str(poster)))
    sections = SectionModel.select(
        SectionModel.id, SectionModel.start, SectionModel.end, SectionModel.track_id
    ).where(SectionModel.video_id == video.id)
    section_durations = [
        (x.end - x.start) / 1000 for x in sections
    ]  # list of sections in seconds
    section_percentage = sum(section_durations) / video.duration * 100
    tracks_created = len([x for x in sections if x.track_id is not None])

    def auto_create_tracks(*args):
        for section in sections:
            if section.track_id is None:
                album = AlbumModel.get_by_id(video.album_id)
                album_item = AlbumItem.from_model(album)
                track = album_item.create_from_section(section=section, video=video)
                section.track_id = track.id
                section.save()

    with solara.Row(justify="center"):
        solara.Text(
            f"{video.title[:80]}",
            classes=["video-info-text"],
        )
    with solara.Columns([6, 6]):
        with solara.Column():
            with solara.Row(justify="center"):
                solara.Image(image, width=IMG_WIDTH)
            with solara.Row(justify="center"):
                solara.Text(
                    f"Uploaded: {time_ago_string(video.upload_date)}",
                    classes=["medium-timer"],
                )
        with solara.Column():
            with solara.Row(justify="center"):
                if len(section_durations) > 0:
                    solara.Markdown(
                        f"Sections: {len(section_durations)} ({section_percentage:.2f}%)"
                    )
                    solara.Markdown(
                        f"Tracks Created: {tracks_created} ({tracks_created / len(section_durations) * 100:.2f}%)"
                    )
                else:
                    solara.Markdown("No Sections Found")
            with solara.Row(justify="center"):
                solara.Text(
                    f"Length: {seconds_to_hms(video.duration)}",
                    classes=["medium-timer"],
                )
            with solara.Row(justify="center"):
                solara.Button(
                    label=f"Create {len(sections)} Tracks",
                    classes=["button"],
                    disabled=(
                        (len(sections) <= tracks_created) or video.album_id is None
                    ),
                    on_click=auto_create_tracks,
                )


@solara.component_vue("../components/video/VideoInfoInputCard.vue")
def VideoInfoInputCard(
    albums,
    serieses,
    youtube_serieses,
    selectedAlbum,
    selectedSeries,
    selectedYoutubeSeries,
    episode_number,
    event_create,
    event_update,
    event_remove,
):
    pass


@solara.component
def InfoPanel(
    video,
):
    force_update_counter = solara.use_reactive(0)
    vid_db = VideoModel.get_by_id(video.id)

    def create(*args):
        logger.debug(f"Generic Create Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]
        except Exception as e:
            logger.error(e)
            return

        try:
            match _type:
                case "album":
                    item_id = AlbumModel.create(**item)
                    vid_db.album = item_id
                    vid_db.save()
                    album_item = AlbumItem.from_model(item_id)
                    album_item.use_video_poster()

                case "series":
                    item_id = SeriesModel.create(**item)
                    vid_db.series = item_id
                    vid_db.save()

                case "youtube_series":
                    item_id = YoutubeSeriesModel.create(**item)
                    vid_db.youtube_series = item_id
                    vid_db.save()

                case _:
                    logger.error(f"Type {_type} not found")
                    return
            force_update_counter.set(force_update_counter.value + 1)

        except Exception as e:
            logger.error(e)
            return

    def update(*args):
        logger.debug(f"Generic Update Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]

        except Exception as e:
            logger.error(e)
            raise

        try:
            match _type:
                case "album":
                    item_id = AlbumModel.get_by_id(item["id"])
                    vid_db.album = item_id
                    vid_db.save()
                    album_item = AlbumItem.from_model(item_id)
                    # i think leaving this here will change the album poster
                    # every time the album is updated
                    album_item.use_video_poster()

                case "series":
                    item_id = SeriesModel.get_by_id(item["id"])
                    vid_db.series = item_id
                    vid_db.save()

                case "youtube_series":
                    item_id = YoutubeSeriesModel.get_by_id(item["id"])
                    vid_db.youtube_series = item_id
                    vid_db.save()

                case _:
                    logger.error(f"Type {_type} not found")
                    return
            force_update_counter.set(force_update_counter.value + 1)

        except Exception as e:
            logger.error(e)
            raise

    def remove(*args):
        logger.debug(f"Generic Remove Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]
        except Exception as e:
            logger.error(e)
            return

        try:
            match _type:
                case "album":
                    other_videos = VideoModel.select().where(
                        (VideoModel.album_id == vid_db.album_id)
                        & (VideoModel.id != video.id)
                    )

                    if len(other_videos) == 0:
                        logger.error(f"Album {vid_db.album_id} not in use. Deleting")
                        vid_db.album.delete_instance()

                    vid_db.album = None

                case "series":
                    other_videos = VideoModel.select().where(
                        (VideoModel.series_id == vid_db.series.id)
                        & (VideoModel.id != video.id)
                    )
                    vid_db.series = None
                    if len(other_videos) == 0:
                        logger.error(
                            f"Series {vid_db.series.name} not in use. Deleting"
                        )
                        vid_db.series.delete_instance()

                case "youtube_series":
                    other_videos = VideoModel.select().where(
                        (VideoModel.youtube_series_id == vid_db.youtube_series.id)
                        & (VideoModel.id != video.id)
                    )
                    vid_db.youtube_series = None
                    if len(other_videos) == 0:
                        logger.error(
                            f"Series {vid_db.youtube_series.title} not in use. Deleting"
                        )
                        vid_db.youtube_series.delete_instance()

                case _:
                    logger.error(f"Type {_type} not found")
                    return

        except Exception as e:
            logger.error(e)
            return

        vid_db.save()
        logger.debug(f"Successfully removed item from video {args}")

    album_dicts = [
        dict(id=a.id, title=a.title)
        for a in AlbumModel.select().order_by(AlbumModel.title)
    ]

    youtube_series_dicts = [
        dict(id=a.id, title=a.title)
        for a in YoutubeSeriesModel.select().order_by(YoutubeSeriesModel.title)
    ]
    series_dicts = [
        dict(id=a.id, name=a.name)
        for a in SeriesModel.select().order_by(SeriesModel.name)
    ]

    try:
        this_album = [a for a in album_dicts if a["id"] == video.album_id][0]
    except IndexError:
        this_album = None

    try:
        this_youtube_series = [
            x for x in youtube_series_dicts if x["id"] == video.youtube_series_id
        ][0]
    except IndexError:
        this_youtube_series = None

    try:
        this_series = [x for x in series_dicts if x["id"] == video.series_id][0]
    except IndexError:
        this_series = None
    if force_update_counter.value >= 0:
        VideoInfoInputCard(
            albums=album_dicts,
            youtube_serieses=youtube_series_dicts,
            serieses=series_dicts,
            selectedAlbum=this_album,
            selectedYoutubeSeries=this_youtube_series,
            selectedSeries=this_series,
            episode_number=video.episode,
            event_create=create,
            event_update=update,
            event_remove=remove,
        ),


# 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
# Jellyfin


@solara.component_vue("../components/video/JellyfinControlPanel.vue")
def JellyfinControlPanel(
    enable_live_updating,
    jellyfin_status,
    event_update_play_state=None,
):
    pass


@solara.component
def JFPanel(
    video,
):

    def refresh_from_jellyfin(*args):
        jellyfin_status_dict.set(get_user_session())

    connected = solara.use_reactive(can_ping_server())
    jellyfin_status_dict = solara.use_reactive(get_user_session())

    JellyfinControlPanel(
        enable_live_updating=connected.value,
        jellyfin_status=jellyfin_status_dict.value,
        page_jellyfin_id=video.jellyfin_id,
        api_key=config["jellyfin"]["api"],
        event_update_play_state=refresh_from_jellyfin,
    )


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    register_vue_components(file=__file__)

    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)

    # should probably be using video.section_ids (not sure if it matters)
    sections = SectionModel.select().where(SectionModel.video_id == video.id)
    reactive_sections.set([s for s in sections])

    jellyfin_status_dict = solara.use_reactive(get_user_session())

    def local_create(*args):
        logger.debug(f"Creating Section: {args}")
        create_section(video, args[0]["start"], args[0]["end"])

    with solara.Column(classes=["main-container"]):
        with solara.Card():
            with solara.Row():
                # VideoInfoInputCard.vue
                # Contains Album, Series, and YT Series 'dialog buttons'
                InfoPanel(
                    video=video,
                )
                # python component - shows full screen file edit dialog
                FilesPanel(
                    video=video,
                )
                # vue component - shows full screen Sections
                # Control Panel dialog
                SectionControlPanel(
                    video=video.serialize(),
                    jellyfin_status=jellyfin_status_dict.value,
                    event_create_section=local_create,
                    event_delete_all_sections=delete_all_sections,
                )

                # # video_details_jf_bar.vue
                JFPanel(
                    video=video,
                )

            with solara.Column():

                # solara component
                VideoInfoPanelLeft(video=video)

            if len(reactive_sections.value) == 0:
                solara.Markdown("No Sections Found")
                if video.album_id is not None:
                    solara.Markdown(f"Album: {video.album_id}")
                else:
                    solara.Markdown(f"Please Create an album before adding sections")
            else:
                SectionsPanel(
                    video=video,
                    reactive_sections=reactive_sections,
                    update_section_from_jellyfin=None,
                )
