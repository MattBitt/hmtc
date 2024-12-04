import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from hmtc.config import init_config
from hmtc.models import (
    Album,
    Artist,
    Beat,
    BeatArtist,
    Channel,
    File,
    FileType,
    Bird,
    BirdFile,
    Playlist,
    Section,
    SectionTopics,
    Series,
    Superchat,
    SuperchatFile,
    SuperchatSegment,
    Topic,
    Track,
    TrackBeat,
    User,
    Video,
    YoutubeSeries,
)
from hmtc.utils.general import get_youtube_id

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

MEDIA_INFO = Path(os.environ.get("HMTC_CONFIG_PATH")) / "media_info"


def create_tables(db, download_info=False):
    db.create_tables(
        [
            Album,
            Artist,
            Beat,
            BeatArtist,
            Channel,
            File,
            Bird,
            BirdFile,
            FileType,
            Playlist,
            Section,
            SectionTopics,
            Series,
            Superchat,
            SuperchatFile,
            SuperchatSegment,
            Topic,
            Track,
            TrackBeat,
            User,
            Video,
            YoutubeSeries,
        ]
    )
    if download_info:
        # 'shouldn't need any more'
        # seed_database()
        pass


def drop_tables(db):
    db.drop_tables(
        [
            Album,
            Artist,
            Beat,
            BeatArtist,
            Channel,
            File,
            FileType,
            Playlist,
            Bird,
            BirdFile,
            Section,
            SectionTopics,
            Series,
            Superchat,
            SuperchatFile,
            SuperchatSegment,
            Topic,
            Track,
            TrackBeat,
            User,
            Video,
            YoutubeSeries,
        ]
    )


def init_db(db, config):
    db.init(
        database=config["database"]["name"],
        user=config["database"]["user"],
        password=config["database"]["password"],
        host=config["database"]["host"],
        port=config["database"]["port"],
    )
    return db


def seed_database():
    import_channels()
    import_series()
    import_playlists()
    import_playlist_info()
    import_youtube_series()


def import_series():
    with open(MEDIA_INFO / "series" / "series.txt", "r") as f:
        series = f.readlines()
        for s in series:
            Series.get_or_create(name=s.strip())
    series = MEDIA_INFO / "series"
    for c in series.glob("*.png"):
        series = Series.get_or_none(Series.name == c.stem)
        if series:
            series.add_file(c, move_file=False)
            logger.success(f"Poster for Series {c.stem} added to db!")
        else:
            logger.error(f"Series {c.stem} not found in db")


def import_youtube_series():
    with open(MEDIA_INFO / "youtube_series.json", "r") as f:
        youtube_series = json.load(f)
        for s in youtube_series:
            original_series = Series.get_or_none(Series.name == s["series_name"])
            if original_series is None:
                logger.error(f"Series {s['series_name']} not found in db")
                continue

            YoutubeSeries.get_or_create(
                title=s["title"].strip(), series=original_series
            )


def import_channels():
    channels = MEDIA_INFO / "channels"
    for c in channels.glob("*info.json"):
        with open(c, "r") as f:
            channel = json.load(f)
            new_channel, created = Channel.get_or_create(
                name=channel["channel"],
                youtube_id=channel["channel_id"],
                url=channel["webpage_url"],
            )
            if created:
                logger.success(f"New Channel {channel['channel']} created")
                new_channel.add_file(c, move_file=False)

            elif new_channel is None:
                logger.warning(
                    f"New Channel {channel['channel']} not created nor found"
                )
                return None
    for c in channels.glob("*.jpg"):
        channel = Channel.get_or_none(Channel.name == c.stem)
        if channel:
            channel.add_file(c, move_file=False)
        else:
            logger.error(f"Channel {c.stem} not found in db")


def import_playlists():
    playlists = MEDIA_INFO / "playlists"
    for p in playlists.glob("*info.json"):
        with open(p, "r") as f:
            playlist = json.load(f)
            channel_id = playlist["channel_id"]
            channel = Channel.get_or_none(Channel.youtube_id == channel_id)

            new_playlist, created = Playlist.get_or_create(
                title=playlist["title"],
                youtube_id=playlist["id"],
                url=playlist["webpage_url"],
                channel=channel,
            )
            if created:
                new_playlist.add_file(p, move_file=False)

    for playlist_image in playlists.glob("*.jpg"):
        playlist = Playlist.get_or_none(Playlist.youtube_id == playlist_image.stem)
        if playlist:
            logger.success(f"Found poster matching playlist {playlist_image.stem}")
            playlist.add_file(playlist_image, move_file=False)
        else:
            logger.error(
                f"Found poster {playlist_image.stem} but no matching playlist found"
            )


def import_playlist_info():
    with open(MEDIA_INFO / "playlists" / "playlists.json", "r") as f:
        playlists_info = json.load(f)
        for p in playlists_info:
            plist = Playlist.get_or_none(title=p["title"])
            series = Series.get_or_none(name=p["series_name"])

            if plist:
                if series:
                    plist.series = series
                plist.enabled = p["enabled"]
                plist.album_per_episode = p["album_per_episode"]
                plist.enable_video_downloads = p["enable_video_downloads"]
                plist.contains_unique_content = p["contains_unique_content"]
                plist.episode_number_template = p.get("episode_number_templates", "")
                plist.save()
            else:
                logger.error(f"Playlist {p['title']} not found in db")


def is_db_empty():
    vids = Video.select(Video.id).count()
    logger.debug(f"DB currently has: {vids} Videos")
    return vids < 10


def import_existing_video_files_to_db(path):
    # havent tested in a million years, but might be a good starting point
    # for the file import
    found = 0
    unfound = 0
    f = Path(path)
    for file in f.glob("**/*.*"):
        if file.is_file():
            youtube_id = get_youtube_id(file.stem)
            if youtube_id:
                vid = Video.get_or_none(Video.youtube_id == youtube_id)
                if not vid:
                    unfound = unfound + 1
                    continue
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
