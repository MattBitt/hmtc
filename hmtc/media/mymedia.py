from datetime import date

OMEGLE = "Omegle Bars"
GUERRILLA = "Guerilla Bars"
LIVESTREAMS = "Livestreams"
LIVESHOWS = "Live Shows"
AD_RAPS = "Ad-Raps"
WRITTENS = "Writtens"
INTERVIEWS = "Interviews/Podcasts"


PLAYLISTS = [
    {
        "name": "Flow State with Harry Mack",
        "url": "https://www.youtube.com/playlist?list=PLtbrIhAJmrPAoGPFsaQn5HCWoO5u4m1La",
        "series_name": INTERVIEWS,
        "album_per_episode": True,
        "episode_number_templates": [],
    },
    {
        "name": "Busking with Bose",
        "url": "https://www.youtube.com/playlist?list=PLtbrIhAJmrPAVe4uNYJZvgkSFk9jKpW1t",
        "series_name": AD_RAPS,
        "album_per_episode": True,
        "episode_number_templates": ["Ep. ([0-9]+)"],
    },
    {
        "name": "Livestream Highlights",
        "url": "https://www.youtube.com/playlist?list=PLtbrIhAJmrPAHZP4a8mtTaoA8Q4D9B8nb",
        "series_name": LIVESTREAMS,
        "album_per_episode": False,
        "album_name": "Livestream Highlights",
        "episode_number_templates": [],
    },
    {
        "name": OMEGLE,
        "url": "https://www.youtube.com/playlist?list=PLtbrIhAJmrPALgw6Ko7H78WxHC3pzxeZl",
        "series_name": OMEGLE,
        "episode_number_templates": [
            "Omegle Bars ([0-9]+)",
            "Omegle Bars Episode ([0-9]+)",
            "Omegle Bars Ep. ([0-9]+)",
        ],
    },
    {
        "name": GUERRILLA,
        "url": "https://www.youtube.com/playlist?list=PLtbrIhAJmrPD7NJ92Jr8s8JFGdmOmMS95",
        "series_name": GUERRILLA,
        "episode_number_templates": [
            "Guerrilla Bars ([0-9]+)",
            "Guerrilla Bars \(Episode ([0-9]+)",
            "Guerrilla Bars Episode ([0-9]+)",
        ],
    },
    {
        "name": "Wordplay Wednesday",
        "url": "https://www.youtube.com/playlist?list=PLtbrIhAJmrPAGLnngi0ZOTvNmuNt5uHJk",
        "series_name": LIVESTREAMS,
        "episode_number_templates": [
            "Wordplay Wednesday \#([0-9]+)",
            "Wordplay Wednesday Episode ([0-9]+)",
            "Wordplay Wednesday w/ Harry Mack.*([0-9]+)",
            "Wordplay Tuesday \#([0-9]+)",
        ],
    },
    {
        "name": "Exclusive Omegle Bars",
        "url": "https://www.youtube.com/playlist?list=PLVuktCy_G9zKL9Ty5HiX33-C8aAoYj6mB",
        "album_per_episode": False,
        "album_name": "Exclusive Omegle Bars",
        "series_name": OMEGLE,
        "episode_number_templates": [],
    },
    {
        "name": "Unreleased Guerilla Bars",
        "url": "https://www.youtube.com/playlist?list=PLVuktCy_G9zJqDdVAuYWwjjvvFfe4xSip",
        "album_per_episode": False,
        "album_name": "Guerilla Bars Unreleased",
        "series_name": GUERRILLA,
        "episode_number_templates": [],
    },
]

SERIES = [
    {
        "name": OMEGLE,
        "start_date": date(2020, 1, 1),
        "end_date": date(2024, 1, 1),
    },
    {
        "name": GUERRILLA,
        "start_date": date(2019, 1, 1),
        "end_date": date(2024, 12, 1),
    },
    {
        "name": LIVESTREAMS,
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 12, 31),
    },
    {
        "name": LIVESHOWS,
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 12, 31),
    },
    {
        "name": INTERVIEWS,
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 12, 31),
    },
    {
        "name": WRITTENS,
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 12, 31),
    },
    {
        "name": AD_RAPS,
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 12, 31),
    },
]
