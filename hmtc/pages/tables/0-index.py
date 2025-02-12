import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons


@solara.component
def Page():

    solara.Markdown("## Domain Object Table Links")

    items = [
        {"text": "Albums", "icon": Icons.ALBUM.value, "url": "/tables/albums"},
        {"text": "Artists", "icon": Icons.USER.value, "url": "/tables/artists"},
        {"text": "Beats", "icon": Icons.BEAT.value, "url": "/tables/beats"},
        {"text": "Channels", "icon": Icons.CHANNEL.value, "url": "/tables/channels"},
        {"text": "Discs", "icon": Icons.DISC.value, "url": "/tables/discs"},
        {"text": "Sections", "icon": Icons.SECTION.value, "url": "/tables/sections"},
        {"text": "Series", "icon": Icons.SERIES.value, "url": "/tables/series"},
        {"text": "Superchats", "icon": Icons.USER.value, "url": "/tables/superchats"},
        {
            "text": "Superchat Segments",
            "icon": Icons.USER.value,
            "url": "/tables/superchat-segments",
        },
        {"text": "Topics", "icon": Icons.TOPIC.value, "url": "/tables/topics"},
        {"text": "Tracks", "icon": Icons.TRACK.value, "url": "/tables/tracks"},
        {"text": "Users", "icon": Icons.USER.value, "url": "/tables/users"},
        {"text": "Videos (Unique)", "icon": Icons.VIDEO.value, "url": "/tables/videos"},
        {
            "text": "Youtube Series",
            "icon": Icons.YOUTUBE_SERIES.value,
            "url": "/tables/youtube-series",
        },
    ]
    with solara.Column(classes=["main-container"]):
        with solara.Link(f"/dashboards/domains"):
            solara.Button("Domains Dashboard", classes=["button"])
        with solara.ColumnsResponsive():
            for item in items:
                with solara.Link(f"{item['url']}"):
                    solara.Button(
                        f"{item['text']}", icon_name=item["icon"], classes=["button"]
                    )
