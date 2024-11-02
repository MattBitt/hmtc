import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Album as AlbumModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.album import Album as AlbumItem


def create_missing_tracks(vids_with_missing_tracks):
    for vid in vids_with_missing_tracks:
        album = AlbumModel.select().where(AlbumModel.id == vid.album_id).get_or_none()
        if album is None:
            logger.error(f"Album not found for video {vid.id}")
            continue
        album_item = AlbumItem.from_model(album)
        sections = SectionModel.select().where(SectionModel.video_id == vid.id)
        for section in sections:
            new_track = album_item.create_from_section(section=section, video=vid)


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    vids = (
        VideoModel.select(
            VideoModel,
            fn.COUNT(SectionModel.id).alias("section_count"),
            fn.SUM((SectionModel.end - SectionModel.start) / 1000).alias(
                "total_sections_duration"
            ),
            fn.COUNT(TrackModel.id).alias("track_count"),
        )
        .join(SectionModel, peewee.JOIN.LEFT_OUTER)
        .join(TrackModel, peewee.JOIN.LEFT_OUTER)
        .group_by(VideoModel.id)
        .where(VideoModel.contains_unique_content == True)
    )
    vids_with_sections = vids.having(fn.COUNT(SectionModel.id) > 0)

    vids_with_equal_sections_and_tracks = vids_with_sections.having(
        fn.COUNT(SectionModel.id) == fn.COUNT(TrackModel.id)
    )
    vids_with_missing_tracks = vids_with_sections.having(
        fn.COUNT(SectionModel.id) > fn.COUNT(TrackModel.id)
    )
    vids_with_missing_tracks_and_no_album = vids_with_missing_tracks.where(
        VideoModel.album_id.is_null()
    )
    vids_with_no_sections = vids.having(fn.COUNT(SectionModel.id) == 0)
    total_tracks = TrackModel.select(fn.COUNT(TrackModel.id)).scalar()
    total_sections = SectionModel.select(fn.COUNT(SectionModel.id)).scalar()
    with solara.Info():
        solara.Markdown(f"# Found {len(vids)} videos with unique content")
        solara.Markdown(f"## {total_tracks} total tracks")
        solara.Markdown(f"## {total_sections} total sections")
        solara.Markdown(f"## {len(vids_with_sections)} videos with sections")
        solara.Markdown(f"## {len(vids_with_no_sections)} with No sections")
    with solara.Success():
        solara.Markdown(
            f"### {len(vids_with_equal_sections_and_tracks)} videos have sections and an equal number of tracks!"
        )
    if len(vids_with_missing_tracks) > 0:
        with solara.Error():
            solara.Markdown(
                f"### {len(vids_with_missing_tracks)} videos with sections created but not enough tracks"
            )
            solara.Markdown(
                f"### {len(vids_with_missing_tracks_and_no_album)} videos are missing tracks AND don't have an album assigned"
            )
            for vid in vids_with_missing_tracks_and_no_album:
                with solara.Link(f"/video-details/{vid.id}"):
                    solara.Markdown(f"### {vid.title}")
            solara.Button(
                label="Create Missing Tracks",
                on_click=lambda: create_missing_tracks(vids_with_missing_tracks),
            )
    else:
        with solara.Success():
            solara.Markdown("### All videos with sections have Tracks created!")
