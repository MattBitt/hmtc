import solara

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.charts.section_stats import SectionStats
from hmtc.domains import (
    Album,
    Artist,
    Beat,
    Channel,
    Disc,
    Section,
    Series,
    Superchat,
    SuperchatSegment,
    Topic,
    Track,
    User,
    Video,
    YoutubeSeries,
)


@solara.component_vue("./DomainCard.vue", vuetify=True)
def DomainCard(
    title: str = "Domain Card", icon: str = Icons.USER.value, value: str = "123"
):
    pass


@solara.component
def Dashboard():

    with solara.Columns([6, 6]):
        with solara.Card():
            with solara.Columns([6, 6]):
                with solara.Link(f"/api/videos"):
                    DomainCard(
                        title="Unique",
                        icon=Icons.VIDEO.value,
                        value=Video.unique_count(),
                    )
                with solara.Link(f"/api/videos"):
                    DomainCard(
                        title="Videos", icon=Icons.VIDEO.value, value=Video.repo.count()
                    )
            with solara.Columns([6, 6]):
                with solara.Link(f"/api/sections"):
                    DomainCard(
                        title="Sections",
                        icon=Icons.SECTION.value,
                        value=Section.repo.count(),
                    )

            with solara.Columns([6, 6]):
                with solara.Link(f"/api/superchats"):
                    DomainCard(
                        title="Superchats",
                        icon=Icons.SUPERCHAT.value,
                        value=Superchat.repo.count(),
                    )
                with solara.Link(f"/api/superchatsegments"):
                    DomainCard(
                        title="Segments",
                        icon=Icons.SUPERCHAT_SEGMENT.value,
                        value=SuperchatSegment.repo.count(),
                    )
        with solara.Card():
            with solara.Link(f"/api/albums"):
                DomainCard(
                    title="Albums", icon=Icons.ALBUM.value, value=Album.repo.count()
                )
            with solara.Columns([6, 6]):
                with solara.Link(f"/api/discs"):
                    DomainCard(
                        title="Discs", icon=Icons.DISC.value, value=Disc.repo.count()
                    )
                with solara.Link(f"/api/tracks"):
                    DomainCard(
                        title="Tracks",
                        icon=Icons.TRACK.value,
                        value=Track.repo.count(),
                    )
        with solara.Column():
            SectionStats()
    with solara.Columns([4, 4, 4]):
        with solara.Link(f"/api/channels"):
            DomainCard(
                title="Channels", icon=Icons.CHANNEL.value, value=Channel.repo.count()
            )
        with solara.Link(f"/api/serieses"):
            DomainCard(
                title="Series", icon=Icons.SERIES.value, value=Series.repo.count()
            )
        with solara.Link(f"/api/topics"):
            DomainCard(title="Topics", icon=Icons.TOPIC.value, value=Topic.repo.count())
        with solara.Link(f"/api/youtubeserieses"):
            DomainCard(
                title="Youtube Series",
                icon=Icons.YOUTUBE_SERIES.value,
                value=YoutubeSeries.repo.count(),
            )
    with solara.Columns([4, 4, 4]):
        with solara.Link(f"/api/beats"):
            DomainCard(title="Beats", icon=Icons.BEAT.value, value=Beat.repo.count())
        with solara.Link(f"/api/artists"):
            DomainCard(
                title="Artists", icon=Icons.USER.value, value=Artist.repo.count()
            )
        with solara.Link(f"/api/users"):
            DomainCard(title="Users", icon=Icons.USER.value, value=User.repo.count())


@solara.component
def Page():
    router = solara.use_router()
    Dashboard()
