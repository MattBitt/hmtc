import json
import os
from datetime import datetime
from pathlib import Path

from loguru import logger

from hmtc.config import init_config
from hmtc.db import create_tables, drop_all_tables, init_db
from hmtc.domains.album import Album
from hmtc.domains.artist import Artist
from hmtc.domains.beat import Beat
from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.series import Series
from hmtc.domains.superchat import Superchat
from hmtc.domains.superchat_segment import SuperchatSegment
from hmtc.domains.topic import Topic
from hmtc.domains.track import Track
from hmtc.domains.user import User
from hmtc.domains.video import Video
from hmtc.domains.youtube_series import YoutubeSeries
from hmtc.models import db_null

config = init_config()


def seed_database():

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
            "id": 5,
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


def seed_database_from_json():
    # HACKY
    db_instance = init_db(db_null, config)
    drop_all_tables(db_instance)
    create_tables(db_instance)
    with open("hmtc/utils/importer/seed_data.json", "r") as f:
        data = json.load(f)
    for channel in data["Channel"]:
        Channel.create(channel)
    for series in data["Series"]:
        Series.create(series)
    for album in data["Album"]:
        Album.create(album)
    for video in data["Video"]:
        Video.create(video)

    # reversed so the 'next' section is created before the 'previous' section
    for section in reversed(data["Section"]):
        Section.create(section)
    for track in data["Track"]:
        Track.create(track)
    for yt_series in data["YoutubeSeries"]:
        YoutubeSeries.create(yt_series)

    for artist in data["Artist"]:
        Artist.create(artist)
    for beat in data["Beat"]:
        Beat.create(beat)

    for superchat in data["Superchat"]:
        Superchat.create(superchat)
    for superchat_segment in reversed(data["SuperchatSegment"]):
        SuperchatSegment.create(superchat_segment)

    for topic in data["Topic"]:
        Topic.create(topic)

    for user in data["User"]:
        User.create(user)
    logger.success("Database seeded from seed_data.json")


def recreate_database(_db):
    logger.debug("Recreating database")
    drop_all_tables(_db)
    create_tables(_db)
    seed_database()
    logger.success("Database recreated")


if __name__ == "__main__":
    seed_database_from_json()
