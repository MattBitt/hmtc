import solara

from hmtc.old_pages.dashboards.domains import Page as DomainsDashboard
from hmtc.old_pages.dashboards.files import Page as FilesDashboard
from hmtc.old_pages.tables.albums import Page as AlbumsPage
from hmtc.old_pages.tables.artists import Page as ArtistsPage
from hmtc.old_pages.tables.beats import Page as BeatsPage
from hmtc.old_pages.tables.channels import Page as ChannelsPage
from hmtc.old_pages.tables.discs import Page as DiscsPage
from hmtc.old_pages.tables.sections import Page as SectionsPage
from hmtc.old_pages.tables.series import Page as SeriesesPage
from hmtc.old_pages.tables.superchat_segments import Page as SuperchatSegmentsPage
from hmtc.old_pages.tables.superchats import Page as SuperchatsPage
from hmtc.old_pages.tables.topics import Page as TopicsPage
from hmtc.old_pages.tables.tracks import Page as TracksPage
from hmtc.old_pages.tables.users import Page as UsersPage
from hmtc.old_pages.tables.videos import VideosPage
from hmtc.old_pages.tables.youtube_series import Page as YoutubeSeriesesPage
from hmtc.old_pages.utils.settings import Page as SettingsPage
from hmtc.pages.albums.details import Page as AlbumDetails
from hmtc.pages.discs.details import Page as DiscDetails
from hmtc.pages.users.main import UsersHomePage
from hmtc.pages.videos.details import Page as VideoDetails
from hmtc.pages.videos.sectionalizer import Page as VideoSectionalizer
from hmtc.pages.videos.video_editor import Page as VideoEditor


def api_routes():
    return solara.Route(
        path="api",
        children=[
            solara.Route(
                path="users",
                children=[
                    solara.Route(
                        path="/",
                        component=UsersPage,
                        label="User's Home",
                    ),
                    solara.Route(
                        path="home",
                        component=UsersHomePage,
                        label="User's Home",
                    ),
                ],
            ),
            solara.Route(
                path="videos",
                children=[
                    solara.Route(
                        path="/",
                        component=VideosPage,
                        label="Video Index",
                    ),
                    solara.Route(
                        path="details",
                        component=VideoDetails,
                        label="Video Details",
                    ),
                    solara.Route(
                        path="editor",
                        component=VideoEditor,
                        label="Video Editor",
                    ),
                    solara.Route(
                        path="sectionalizer",
                        component=VideoSectionalizer,
                        label="Sectionalizer",
                    ),
                ],
            ),
            solara.Route(
                path="albums",
                children=[
                    solara.Route(
                        path="/",
                        component=AlbumsPage,
                        label="Album Index",
                    ),
                    solara.Route(
                        path="details",
                        component=AlbumDetails,
                        label="Album Details",
                    ),
                ],
            ),
            solara.Route(
                path="discs",
                children=[
                    solara.Route(
                        path="/",
                        component=DiscsPage,
                        label="Disc Index",
                    ),
                    solara.Route(
                        path="details",
                        component=DiscDetails,
                        label="Disc Details",
                    ),
                ],
            ),
            solara.Route(
                path="topics",
                children=[
                    solara.Route(
                        path="/",
                        component=TopicsPage,
                        label="Topic Index",
                    ),
                ],
            ),
            solara.Route(
                path="sections",
                children=[
                    solara.Route(
                        path="/",
                        component=SectionsPage,
                        label="Section Index",
                    ),
                ],
            ),
            solara.Route(
                path="channels",
                children=[
                    solara.Route(
                        path="/",
                        component=ChannelsPage,
                        label="Channel Index",
                    ),
                ],
            ),
            solara.Route(
                path="serieses",
                children=[
                    solara.Route(
                        path="/",
                        component=SeriesesPage,
                        label="Series Index",
                    ),
                ],
            ),
            solara.Route(
                path="youtubeserieses",
                children=[
                    solara.Route(
                        path="/",
                        component=YoutubeSeriesesPage,
                        label="Youtube Series Index",
                    ),
                ],
            ),
            solara.Route(
                path="tracks",
                children=[
                    solara.Route(
                        path="/",
                        component=TracksPage,
                        label="Track Index",
                    ),
                ],
            ),
            solara.Route(
                path="beats",
                children=[
                    solara.Route(
                        path="/",
                        component=BeatsPage,
                        label="Beat Index",
                    ),
                ],
            ),
            solara.Route(
                path="artists",
                children=[
                    solara.Route(
                        path="/",
                        component=ArtistsPage,
                        label="Artist Index",
                    ),
                ],
            ),
            solara.Route(
                path="superchats",
                children=[
                    solara.Route(
                        path="/",
                        component=SuperchatsPage,
                        label="Superchat Index",
                    ),
                ],
            ),
            solara.Route(
                path="superchatsegments",
                children=[
                    solara.Route(
                        path="/",
                        component=SuperchatSegmentsPage,
                        label="Superchat Segment Index",
                    ),
                ],
            ),
        ],
    )


def admin_routes():
    return solara.Route(
        path="admin",
        children=[
            solara.Route(
                path="settings",
                component=SettingsPage,
                label="Settings",
            ),
            solara.Route(
                path="dashboards",
                children=[
                    solara.Route(
                        path="domains",
                        component=DomainsDashboard,
                        label="Admin",
                    ),
                    solara.Route(
                        path="files",
                        component=FilesDashboard,
                        label="Files Dashboard",
                    ),
                ],
            ),
        ],
    )
