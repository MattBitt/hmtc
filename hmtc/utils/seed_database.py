from datetime import datetime

from loguru import logger

from hmtc.db import create_tables, drop_all_tables
from hmtc.domains.album import Album
from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.series import Series
from hmtc.domains.track import Track
from hmtc.domains.video import Video
from hmtc.domains.youtube_series import YoutubeSeries


def seed_database():
    # this is a good starting point for seeding the database
    # with some initial data

    channels = [
        {
            "title": "Harry Mack",
            "url": "https://www.youtube.com/@HarryMack",
            "youtube_id": "UC59ZRYCHev_IqjUhremZ8Tg",
            "auto_update": True,
        },
        {
            "title": "Harry Mack Clips",
            "url": "https://www.youtube.com/@HarryMackClips",
            "youtube_id": "UCcnAEyz9VnlBL1DiQqliJkQ",
            "auto_update": True,
        },
    ]

    for channel_dict in channels:
        Channel.create(channel_dict)

    # trying to use series as the 'type' of audience for his performances
    series = [
        "Omegle",
        "Guerrilla",
        "Busking",
        "Concert",
        "Interview",
        "Livestream",
        "Written",
        "Advertisement",
    ]
    start = datetime(2021, 1, 1)
    end = datetime(2021, 12, 31)
    for s in series:
        Series.create({"title": s, "start_date": start, "end_date": end})

    youtube_serieses = [
        {"title": "Omegle Bars", "series": "Omegle"},
        {"title": "Guerrilla Bars", "series": "Guerrilla"},
        {"title": "Wordplay Wednesday", "series": "Livestream"},
    ]

    for yts in youtube_serieses:
        YoutubeSeries.create(yts)

    albums = [
        {"title": "Omegle Bars", "release_date": "2024-09-23"},
        {"title": "Guerrilla Bars", "release_date": "2023-09-23"},
        {"title": "Wordplay Wednesday", "release_date": datetime(2021, 12, 31)},
    ]
    for album in albums:
        Album.create(album)

    vids = [
        {
            "description": "Omegle Bars 1 (initial Source)",
            "duration": 1500,
            "title": "Omegle Bars 1 (initial Source)",
            "unique_content": True,
            "upload_date": "2021-01-01",
            "url": "https://www.youtube.com/watch?v=1234",
            "youtube_id": "1234",
            "episode": 1,
            "channel": "Harry Mack",
            "series": "Livestream",
            "youtube_series": "Omegle Bars",
            "album": "Omegle Bars",
        },
        {
            "description": "Omegle Bars 1 (initial Source)",
            "duration": 4000,
            "title": "DELETE ME ME ME (second)",
            "unique_content": True,
            "upload_date": "2023-01-01",
            "url": "https://www.youtube.com/watch?v=1234zxcvasd",
            "youtube_id": "1234cvdde",
            "episode": None,
            "channel": "Harry Mack",
            "series": "Livestream",
            "youtube_series": "Wordplay Wednesday",
            "album": "Wordplay Wednesday",
        },
        {
            "description": "Omegle Bars 1 (initial Source)",
            "duration": 1200,
            "title": "Guerrilla Bars 17 (initial Source)",
            "unique_content": True,
            "upload_date": "2024-01-01",
            "url": "https://www.youtube.com/watch?v=84561564",
            "youtube_id": "358741",
            "episode": 0,
            "channel": "Harry Mack",
            "series": "Guerrilla",
            "youtube_series": "Guerrilla Bars",
            "album": "Guerrilla Bars",
        },
    ]
    for vid in vids:
        Video.create(vid)

    sections = [
        {
            "start": 100,
            "end": 400,
            "section_type": "verse",
            "video": vids[0]["title"],
        },
        {
            "start": 500,
            "end": 900,
            "section_type": "verse",
            "video": vids[0]["title"],
        },
        {
            "start": 1000,
            "end": 1300,
            "section_type": "verse",
            "video": vids[0]["title"],
        },
        {
            "start": 0,
            "end": 400,
            "section_type": "verse",
            "video": vids[1]["title"],
        },
        {
            "start": 0,
            "end": 400,
            "section_type": "verse",
            "video": vids[2]["title"],
        },
    ]

    tracks = [
        {
            "id": 1,
            "title": "OB 1 - Verse 1",
            "track_number": 1,
            "length": 45,
            "album": albums[0]["title"],
            "video": vids[0]["title"],
        },
        {
            "id": 2,
            "title": "OB 1 - Verse 2",
            "track_number": 2,
            "length": 142,
            "album": albums[0]["title"],
            "video": vids[0]["title"],
        },
        {
            "id": 3,
            "title": "OB 1 - Verse 3",
            "track_number": 1,
            "length": 543,
            "album": albums[0]["title"],
            "video": vids[0]["title"],
        },
        {
            "id": 4,
            "title": "My Third Track",
            "track_number": 1,
            "length": 657,
            "album": albums[1]["title"],
            "video": vids[1]["title"],
        },
        {
            "id": 4,
            "title": "Another Track from a vid",
            "track_number": 1,
            "length": 432,
            "album": albums[2]["title"],
            "video": vids[2]["title"],
        },
    ]
    for section in sections:
        sect = Section.create(section)
        for track in tracks:
            if track["video"] == section["video"].title:
                track["section"] = sect.id
                Track.create(track)


def recreate_database(_db):
    logger.debug("Recreating database")
    drop_all_tables(_db)
    create_tables(_db)
    seed_database()
    logger.success("Database recreated")
