import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from hmtc.models import (
    Album,
    AlbumFile,
    Artist,
    ArtistFile,
    Beat,
    BeatArtist,
    Channel,
    ChannelFile,
    EpisodeNumberTemplate,
    File,
    Playlist,
    PlaylistAlbum,
    PlaylistFile,
    PlaylistVideo,
    Post,
    Section,
    Series,
    SeriesFile,
    Track,
    TrackBeat,
    TrackFile,
    User,
    UserInfo,
    Video,
    VideoFile,
)
from hmtc.utils.general import csv_to_dict, get_youtube_id

MEDIA_INFO = Path(os.environ.get("HMTC_CONFIG_PATH")) / "media_info"


def create_video_sections():
    for vid in Video.select():
        if vid.sections == []:
            vid.create_initial_section()


def init_db(db, config):
    db.init(
        database=config["database"]["name"],
        user=config["database"]["user"],
        password=config["database"]["password"],
        host=config["database"]["host"],
        port=config["database"]["port"],
    )
    return db


def import_series():
    with open(MEDIA_INFO / "series.txt", "r") as f:
        series = f.readlines()
        for s in series:
            Series.create(name=s.strip())


def import_playlists():
    playlists = MEDIA_INFO / "playlists"
    for p in playlists.glob("*info.json"):
        with open(p, "r") as f:
            playlist = json.load(f)
            Playlist.create(
                title=playlist["title"],
                youtube_id=playlist["id"],
                url=playlist["webpage_url"],
            )


def import_channels():
    channels = MEDIA_INFO / "channels"
    for c in channels.glob("*info.json"):
        with open(c, "r") as f:
            channel = json.load(f)
            Channel.create(
                name=channel["channel"],
                youtube_id=channel["channel_id"],
                url=channel["webpage_url"],
            )


def create_tables(db):
    db.create_tables(
        [
            Playlist,
            ChannelFile,
            Video,
            Series,
            Album,
            Track,
            EpisodeNumberTemplate,
            File,
            Beat,
            BeatArtist,
            TrackBeat,
            Artist,
            Section,
            User,
            UserInfo,
            Post,
            PlaylistVideo,
            PlaylistAlbum,
            VideoFile,
            ArtistFile,
            SeriesFile,
            AlbumFile,
            TrackFile,
            Channel,
            PlaylistFile,
        ]
    )
    s = Series.get_or_none()
    if not s:
        import_series()
    p = Playlist.get_or_none()
    if not p:
        import_playlists()
    c = Channel.get_or_none()
    if not c:
        import_channels()


def drop_tables(db):
    db.drop_tables(
        [
            Playlist,
            ChannelFile,
            Video,
            Series,
            Album,
            Track,
            EpisodeNumberTemplate,
            File,
            Beat,
            BeatArtist,
            TrackBeat,
            Artist,
            Section,
            User,
            UserInfo,
            Post,
            PlaylistVideo,
            PlaylistAlbum,
            VideoFile,
            ArtistFile,
            SeriesFile,
            AlbumFile,
            TrackFile,
            Channel,
            PlaylistFile,
        ]
    )


def is_db_empty(db):
    return len(db.get_tables()) == 0


def get_playlist(playlist: dict):
    try:
        return Playlist.get(Playlist.title == playlist["name"])
    except Playlist.DoesNotExist:
        logger.info(f"Playlist {playlist['name']} not found in db")
        return None
    except Exception as e:
        logger.error(f"Error getting playlist from db: {e}")
        return None


def get_list_yt_playlists():
    playlists = []
    for p in Playlist.select().where(Playlist.enabled == True).order_by(Playlist.title):
        playlists.append(p.name)
    return playlists


def get_list_videos():
    videos = []
    for v in Video.select().where(Video.private == False).order_by(Video.title):
        videos.append(v.title)
    return videos


def get_series(series: str):
    try:
        return Series.get(Series.name == series)
    except Series.DoesNotExist:
        logger.info(f"Series {series} not found in db")
        return None
    except Exception as e:
        logger.error(f"Error getting series from db: {e}")
        return None


def import_existing_video_files_to_db(path):
    # probably only need this to get the existing files
    # scaffoled (sp) into the database
    found = 0
    unfound = 0
    f = Path(path)
    for file in f.glob("**/*.*"):
        if file.is_file():
            file_info = {}
            youtube_id = get_youtube_id(file.stem)
            if youtube_id:
                vid = Video.get_or_none(Video.youtube_id == youtube_id)
                if not vid:
                    # logger.debug(
                    #     f"Video not currently in db {video_info['youtube_id']}"
                    # )
                    unfound = unfound + 1
                    continue

                    # file_info["video"] = vid
                    # file_info["local_path"] = str(path)
                    # file_info["filename"] = file.stem
                    # file_info["extension"] = file.suffix
                    # file_info["downloaded"] = True

                    # file = File.create(**file_info)
                else:
                    logger.debug(
                        f"Successfully found video{vid.youtube_id}. Adding file"
                    )
            else:
                logger.debug(f"Could not find youtube_id in {file}")

    logger.success("Finished importing files to the database.")
    logger.debug(f"Found {found} new files.")
    logger.debug(f"There were {unfound} files found with no associated video")

    if not f.exists():
        logger.error("Path not found")
        return None
    return f.glob("**/*")


def import_existing_tracks(filename):
    # these aren't really tracks.

    if not Path(filename).exists():
        logger.error(f"Track CSV not found {filename}")
    tracks = csv_to_dict(filename)
    for track in tracks:
        video = Video.get_or_none(Video.youtube_id == track["youtube_id"])

        if not video:
            # logger.error(f"Video not found to for this track {track}")
            continue
        if not video.sections:
            logger.error("Video has no initial section created in the DB.")
            continue

        if len(video.sections) > 1:
            logger.error(
                "New sections (after the initial) have already been created. Skipping import"
            )
            continue
        # for each 'track' insert a section break at the beginning
        # and at the end timestamps. mark the previous section
        # as talking, and the new section as music
        start_ts = int(track["start"])
        video.add_section_break(timestamp=start_ts)
        end_ts = int(track["end"])
        video.add_section_break(timestamp=end_ts)

        # using the ts +/- 5 below to not worry about edge cases
        # when the section is or isn't on the section break

        # section before the track
        prev_section_timestamp = start_ts - 5
        if prev_section_timestamp < 0:
            prev_section_timestamp = 0
        section = video.get_section_with_timestamp(timestamp=(prev_section_timestamp))
        section.section_type = "talking"
        section.save()

        # section containing the track
        section = video.get_section_with_timestamp(timestamp=(start_ts + 5))
        section.section_type = "music"
        section.save()

        # should also create a Track object with the words and stuff
        # but it shouldn't know anything about its position
        # within the Video (start/end)


def update_playlist(playlist, download_path="./downloads", media_path="./media"):
    now = datetime.now()
    logger.debug(
        f"📕📕📕{playlist.name} was updated at {playlist.last_update_completed}"
    )
    last_completed = playlist.last_update_completed
    if not last_completed or (now - last_completed > timedelta(hours=2)):
        playlist.check_for_new_videos(download_path, media_path)


def update_playlists(config):
    logger.debug("Updating playlists")
    playlists = Playlist().select().join(Series).where(Playlist.enabled == True)
    download_path = config.get("GENERAL", "DOWNLOAD_PATH")
    media_path = config.get("PATHS", "MEDIA")
    for p in playlists:
        update_playlist(p, download_path, media_path)
