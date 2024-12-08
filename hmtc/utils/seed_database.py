from datetime import datetime
from hmtc.domains.channel import Channel
from hmtc.domains.series import Series
from hmtc.db import create_tables, drop_all_tables


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
        c = Channel.create(channel_dict)

    # try to use series as the 'type' of audience for his performances
    series = [
        "Guerrilla Bars",
        "Busking",
        "Concert",
        "Interview",
        "Livestream",
        "Written",
    ]
    start = datetime(2021, 1, 1)
    end = datetime(2021, 12, 31)
    for s in series:

        Series.create({"title": s, "start_date": start, "end_date": end})
    youtube_serieses = ["Omegle Bars", "Guerilla Bars", "Wordplay Wednesday"]


def recreate_database(_db):
    drop_all_tables(_db)
    create_tables(_db)
    seed_database()
