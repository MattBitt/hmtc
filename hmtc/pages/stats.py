import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Album as AlbumModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    solara.Markdown(f"# Stats")
    # Query to get all unique videos along with their sections, albums, and tracks
    vids = VideoModel.select(VideoModel).where(
        VideoModel.contains_unique_content == True
    )

    info_dicts = []
    solara.Markdown(f"# {len(vids)} videos")
    for vid in vids:
        sections = SectionModel.select().where(SectionModel.video_id == vid.id)
        total_section_duration = sum([(s.end - s.start) / 1000 for s in sections])

        info = {}
        info["id"] = vid.id
        info["title"] = vid.title
        info["num_sections"] = len(vid.sections)
        info["num_tracks"] = None
        info["sections_percent_created"] = total_section_duration / vid.duration
        info_dicts.append(info)

    solara.Markdown("## Videos")
