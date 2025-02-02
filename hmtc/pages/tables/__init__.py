import solara
from loguru import logger



@solara.component
def Page():
    router = solara.use_router()

    solara.Markdown("## Domain Object Table Links")

    items = [
        {"text": "Albums", "icon": "mdi-album", "url": "/tables/albums"},
        {"text": "Artists", "icon": "mdi-account", "url": "/tables/artists"},
        {"text": "Beats", "icon": "mdi-music", "url": "/tables/beats"},
        {"text": "Channels", "icon": "mdi-view-list", "url": "/tables/channels"},
        {"text": "Discs", "icon": "mdi-disc", "url": "/tables/discs"},
        {"text": "Sections", "icon": "mdi-rhombus-split", "url": "/tables/sections"},
        {"text": "Series", "icon": "mdi-shape", "url": "/tables/series"},
        {"text": "Superchats", "icon": "mdi-account", "url": "/tables/superchats"},
        {
            "text": "Superchat Segments",
            "icon": "mdi-account",
            "url": "/tables/superchat-segments",
        },
        {"text": "Topics", "icon": "mdi-book-open", "url": "/tables/topics"},
        {"text": "Tracks", "icon": "mdi-music-clef-treble", "url": "/tables/tracks"},
        {"text": "Users", "icon": "mdi-account", "url": "/tables/users"},
        {"text": "Videos (Unique)", "icon": "mdi-video", "url": "/tables/videos"},
        {
            "text": "Youtube Series",
            "icon": "mdi-youtube",
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


@solara.component
def Layout(children=[]):
    with solara.AppLayout(children=children, navigation=False):
        with solara.Row():
            solara.Text(f"Some text in the tables layout")