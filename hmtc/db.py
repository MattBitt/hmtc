from loguru import logger
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
    db,
)
from hmtc.media.mymedia import PLAYLISTS, SERIES
from pathlib import Path
from hmtc.utils.general import parse_video_file_name, csv_to_dict


# try:
#     User.create_table()
#     UserInfo.create_table()
#     Post.create_table()
# except:
#     pass


def setup_db(config):
    db_path = config.get("DATABASE", "PATH")

    db.init(
        db_path,
        pragmas={
            "journal_mode": "wal",
            "cache_size": 10000,
            "foreign_keys": 1,
        },
    )
    db.connect()

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
        ]
    )
    seed_database()
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
        if not Playlist.get_or_none(Playlist.url == playlist_info["url"]):

            # remove the template strings in order to save them in
            # their own table in the db
            templates = playlist_info.pop("episode_number_templates")

            playlist = Playlist.create(**playlist_info)
            playlist.series = series
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

    logger.success(f"Finished importing files to the database.")
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
