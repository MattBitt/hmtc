import solara

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
    title: str = "Domain Card", icon: str = "mdi-account", value: str = "123"
):
    pass


@solara.component
def Dashboard():
    with solara.Columns([6, 6]):
        with solara.Card():
            with solara.Columns([6, 6]):
                DomainCard(title="Unique", icon="mdi-video", value=Video.unique_count())
                DomainCard(title="Videos", icon="mdi-video", value=Video.repo.count())
            with solara.Columns([6, 6]):
                DomainCard(
                    title="Sections",
                    icon="mdi-rhombus-split",
                    value=Section.repo.count(),
                )

                DomainCard(
                    title="Topics", icon="mdi-book-open", value=Topic.repo.count()
                )
            with solara.Columns([6, 6]):
                DomainCard(
                    title="Superchats", icon="mdi-comment", value=Superchat.repo.count()
                )
                DomainCard(
                    title="Segments",
                    icon="mdi-comment",
                    value=SuperchatSegment.repo.count(),
                )
        with solara.Card():
            DomainCard(title="Albums", icon="mdi-album", value=Album.repo.count())
            with solara.Columns([6, 6]):
                DomainCard(title="Discs", icon="mdi-disc", value=Disc.repo.count())
                DomainCard(
                    title="Tracks",
                    icon="mdi-music-clef-treble",
                    value=Track.repo.count(),
                )
    with solara.Columns([4, 4, 4]):
        DomainCard(title="Channels", icon="mdi-view-list", value=Channel.repo.count())
        DomainCard(title="Series", icon="mdi-shape", value=Series.repo.count())
        DomainCard(
            title="Youtube Series", icon="mdi-youtube", value=YoutubeSeries.repo.count()
        )
    with solara.Columns([4, 4, 4]):
        DomainCard(title="Beats", icon="mdi-music", value=Beat.repo.count())
        DomainCard(title="Artists", icon="mdi-account", value=Artist.repo.count())
        DomainCard(title="Users", icon="mdi-account", value=User.repo.count())


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    Dashboard()
