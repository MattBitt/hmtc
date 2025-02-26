from loguru import logger

from hmtc.models import *

TABLES = [
    Album,
    OmegleSection,
    AlbumFiles,
    Artist,
    AudioFile,
    Beat,
    BeatArtist,
    Channel,
    ChannelFiles,
    Disc,
    DiscVideo,
    InfoFile,
    ImageFile,
    Section,
    SectionTopic,
    Series,
    SubtitleFile,
    LyricsFile,
    Superchat,
    SuperchatSegment,
    Thumbnail,
    Topic,
    Track,
    TrackBeat,
    TrackFiles,
    User,
    Video,
    VideoFile,
    VideoFiles,
    YoutubeSeries,
    YoutubeSeriesVideo,
]


def create_tables(db, tables=[]):
    if not tables:
        tables = TABLES
    db.create_tables(tables)


def drop_all_tables(db):
    db.drop_tables(TABLES)


def init_db(db, config):
    db.init(
        database=config["database"]["name"],
        user=config["database"]["user"],
        password=config["database"]["password"],
        host=config["database"]["host"],
        port=config["database"]["port"],
    )

    return db
