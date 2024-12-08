from datetime import datetime

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
            "description": "DELETEME",
            "duration": 500,
            "title": "DELETE ME ME ME (FIRST)",
            "unique_content": True,
            "upload_date": "2021-01-01",
            "url": "https://www.youtube.com/watch?v=1234",
            "youtube_id": "1234",
            "episode": 1,
            "channel": "Harry Mack",
            "series": "Guerrilla",
            "youtube_series": "Guerrilla Bars",
            "album": "Guerrilla Bars",
        },
        {
            "description": "DELETEME",
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
            "description": "DELETEME",
            "duration": 1200,
            "title": "DELETE ME ME ME (LAST)",
            "unique_content": True,
            "upload_date": "2024-01-01",
            "url": "https://www.youtube.com/watch?v=12345678",
            "youtube_id": "123781",
            "episode": 0,
            "channel": "Harry Mack",
            "series": "Concert",
            "youtube_series": "Omegle Bars",
            "album": "Omegle Bars",
        },
    ]
    for vid in vids:
        Video.create(vid)

    sections = [
        {
            "start": 0,
            "end": 400,
            "section_type": "verse",
            "video": "DELETE ME ME ME (FIRST)",
            "track_id": 1,
        },
        {
            "start": 0,
            "end": 400,
            "section_type": "verse",
            "video": "DELETE ME ME ME (second)",
            "track_id": 2,
        },
        {
            "start": 0,
            "end": 400,
            "section_type": "verse",
            "video": "DELETE ME ME ME (LAST)",
            "track_id": 3,
        },
    ]
    for section in sections:
        Section.create(section)
    tracks = [
        {
            "id": 1,
            "title": "My First Track",
            "track_number": 1,
            "length": 45,
            "album": "Omegle Bars",
            "video": "DELETE ME ME ME (second)",
        },
        {
            "id": 2,
            "title": "My Second Track",
            "track_number": 2,
            "length": 45,
            "album": "Omegle Bars",
            "video": "DELETE ME ME ME (second)",
        },
        {
            "id": 3,
            "title": "My Third Track",
            "track_number": 3,
            "length": 45,
            "album": "Guerrilla Bars",
            "video": "DELETE ME ME ME (FIRST)",
        },
    ]
    for track in tracks:
        Track.create(track)


def recreate_database(_db):
    drop_all_tables(_db)
    create_tables(_db)
    seed_database()
