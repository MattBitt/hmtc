from loguru import logger
from hmtc.config import init_config
from hmtc.models import (
    Playlist,
    Video,
    Series,
    Album,
    Track,
    EpisodeNumberTemplate,
    File,
    Artist,
    Beat,
    BeatArtist,
    TrackBeat,
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
    ChannelVideo,
    db,
)
from hmtc.media.mymedia import PLAYLISTS, SERIES, CHANNELS
from pathlib import Path
from hmtc.utils.general import parse_video_file_name, csv_to_dict
from datetime import timedelta, datetime


def create_video_sections():
    for vid in Video.select():
        if vid.sections == []:
            vid.create_initial_section()


def create_tables():

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
            ChannelVideo,
        ]
    )
    return db


def get_playlist(playlist: dict):
    try:
        return Playlist.get(Playlist.name == playlist["name"])
    except Playlist.DoesNotExist:
        logger.info(f"Playlist {playlist['name']} not found in db")
        return None
    except Exception as e:
        logger.error(f"Error getting playlist from db: {e}")
        return None


def get_list_yt_playlists():
    playlists = []
    for p in Playlist.select().where(Playlist.enabled == True).order_by(Playlist.name):
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


def seed_database():
    # imports all manually entered data to get a new database up an running
    # be aware that this won't save any of the downloaded data
    # return
    for channel_info in CHANNELS:
        channel = Channel().get_or_none(Channel.name == channel_info["name"])
        if not channel:
            Channel.create(**channel_info)

    for series_info in SERIES:
        series = Series().get_or_none(Series.name == series_info["name"])
        if not series:
            Series.create(**series_info)

    for playlist_info in PLAYLISTS:
        # in order to add a playlist to the db it should adhere to the following
        # url not in db
        # needs to be associated with:
        # a series (always)
        # an album (if album_per_episode is false)
        series = Series.get_or_none(Series.name == playlist_info.pop("series_name"))

        if not series:
            logger.error(
                f"Series ({playlist_info['series_name']} for playlist {playlist_info['name']}) not found. Skipping Playlist"
            )
            continue

        channel = Channel.get_or_none(Channel.name == playlist_info.pop("channel_name"))
        if not channel:
            logger.error(
                f"Channel ({playlist_info['channel_name']} for playlist {playlist_info['name']}) not found. Skipping Playlist"
            )
            continue

        if not Playlist.get_or_none(Playlist.url == playlist_info["url"]):

            # remove the template strings in order to save them in
            # their own table in the db
            templates = playlist_info.pop("episode_number_templates")

            playlist = Playlist.create(**playlist_info)
            playlist.series = series
            playlist.channel = channel
            playlist.save()

            for template in templates:
                EpisodeNumberTemplate.create(template=template, playlist=playlist)


def import_existing_video_files_to_db(path):
    # probably only need this to get the existing files
    # scaffoled (sp) into the database
    found = 0
    unfound = 0
    f = Path(path)
    for file in f.glob("**/*mkv*"):
        if file.is_file():
            file_info = {}
            video_info = parse_video_file_name(file)
            if video_info:
                vid = Video.get_or_none(Video.youtube_id == video_info["youtube_id"])
                if not vid:
                    # logger.debug(
                    #     f"Video not currently in db {video_info['youtube_id']}"
                    # )
                    unfound = unfound + 1
                    continue

                if not vid.files:
                    found = found + 1
                    file_info["video"] = vid
                    file_info["local_path"] = str(path)
                    file_info["filename"] = file.stem
                    file_info["extension"] = file.suffix
                    file_info["downloaded"] = True

                    file = File.create(**file_info)
                else:
                    # logger.debug(
                    #     "This video already has files associated. Skipping import"
                    # )
                    continue
            else:
                unfound = unfound + 1

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
    media_path = config.get("MEDIA", "VIDEO_PATH")
    for p in playlists:
        update_playlist(p, download_path, media_path)


def seed_empty_database(config):
    logger.debug("Seeding Database")
    seed_database()

    # logger.debug("Creating initial sections in each video")
    # create_video_sections()

    # logger.debug("Creating sections from track data")
    # track_csv = config.get("IMPORT", "TRACK_INFO")
    # import_existing_tracks(track_csv)  # turns the 'track' info into sections

    # video_path = config.get("MEDIA", "VIDEO_PATH")
    # import_existing_video_files_to_db(video_path)


if __name__ == "__main__":
    # this creates a db from scratch
    # only to be used for fresh data instance
    config = init_config()

    create_tables()

    # seed_empty_database(config)
    # print("updating playlist")
    # update_playlists(config)
