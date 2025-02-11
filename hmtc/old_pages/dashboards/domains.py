import solara

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared.sidebar import MySidebar
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
                DomainCard(
                    title="Unique", icon=Icons.VIDEO.value, value=Video.unique_count()
                )
                DomainCard(
                    title="Videos", icon=Icons.VIDEO.value, value=Video.repo.count()
                )
            with solara.Columns([6, 6]):
                DomainCard(
                    title="Sections",
                    icon=Icons.SECTION.value,
                    value=Section.repo.count(),
                )

                DomainCard(
                    title="Topics", icon=Icons.TOPIC.value, value=Topic.repo.count()
                )
            with solara.Columns([6, 6]):
                DomainCard(
                    title="Superchats",
                    icon=Icons.SUPERCHAT.value,
                    value=Superchat.repo.count(),
                )
                DomainCard(
                    title="Segments",
                    icon=Icons.SUPERCHAT_SEGMENT.value,
                    value=SuperchatSegment.repo.count(),
                )
        with solara.Card():
            DomainCard(title="Albums", icon=Icons.ALBUM.value, value=Album.repo.count())
            with solara.Columns([6, 6]):
                DomainCard(
                    title="Discs", icon=Icons.DISC.value, value=Disc.repo.count()
                )
                DomainCard(
                    title="Tracks",
                    icon=Icons.TRACK.value,
                    value=Track.repo.count(),
                )
    with solara.Columns([4, 4, 4]):
        DomainCard(
            title="Channels", icon=Icons.CHANNEL.value, value=Channel.repo.count()
        )
        DomainCard(title="Series", icon=Icons.SERIES.value, value=Series.repo.count())
        DomainCard(
            title="Youtube Series",
            icon=Icons.YOUTUBE_SERIES.value,
            value=YoutubeSeries.repo.count(),
        )
    with solara.Columns([4, 4, 4]):
        DomainCard(title="Beats", icon=Icons.BEAT.value, value=Beat.repo.count())
        DomainCard(title="Artists", icon=Icons.USER.value, value=Artist.repo.count())
        DomainCard(title="Users", icon=Icons.USER.value, value=User.repo.count())


@solara.component
def Page():
    router = solara.use_router()
    Dashboard()
