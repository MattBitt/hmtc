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
    Breakpoint,
    Channel,
    EpisodeNumberTemplate,
    File,
    Playlist,
    PlaylistAlbum,
    Post,
    Section,
    Series,
    TodoTable,
    Track,
    TrackBeat,
    User,
    UserInfo,
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
            Playlist,
            Video,
            Series,
            Album,
            Track,
            EpisodeNumberTemplate,
            File,
            Beat,
            BeatArtist,
            TrackBeat,
            Breakpoint,
            Artist,
            Section,
            User,
            UserInfo,
            Post,
            PlaylistAlbum,
            Channel,
            TodoTable,
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
            Playlist,
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
            Breakpoint,
            Section,
            User,
            UserInfo,
            Post,
            PlaylistAlbum,
            Channel,
            TodoTable,
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


def download_channel_videos():
    logger.warning("Download List of Videos for channel. Please wait...")
    logger.warning(
        "To disable these checks, set the 'download_on_init' config to False"
    )
    channels = Channel.select().where(Channel.enabled is True)
    for channel in channels:
        channel.check_for_new_videos()


def download_playlist_videos():
    logger.warning("Download List of Videos for playlist. Please wait...")
    logger.warning(
        "To disable these checks, set the 'download_on_init' config to False"
    )
    playlists = Playlist.select().where(Playlist.enabled is True)
    for playlist in playlists:
        playlist.update_videos_with_playlist_info()


def is_db_empty():

    vids = Video.select().count()
    logger.debug(f"DB currently has: {vids} Videos")
    return vids < 10


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
    for p in Playlist.select().where(Playlist.enabled is True).order_by(Playlist.title):
        playlists.append(p.name)
    return playlists


def get_list_videos():
    videos = []
    for v in Video.select().where(Video.private is False).order_by(Video.title):
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
    playlists = Playlist().select().join(Series).where(Playlist.enabled is True)
    download_path = WORKING / "downloads"
    media_path = STORAGE / "media"

    for p in playlists:
        update_playlist(p, download_path, media_path)
