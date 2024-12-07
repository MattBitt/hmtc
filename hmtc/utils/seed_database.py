from hmtc.domains.channel import Channel


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
    youtube_serieses = ["Omegle Bars", "Guerilla Bars", "Wordplay Wednesday"]
