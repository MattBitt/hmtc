from pathlib import Path

import solara

from hmtc.components.multi_select import MultiSelect
from hmtc.components.single_select import SingleSelect
from hmtc.models import Playlist, Series, Video
from hmtc.config import init_config

all_series = [s.name for s in Series.select()]
selected_series = solara.reactive(all_series)


all_playlists = [p.title for p in Playlist.select()]
selected_playlist = solara.reactive(all_playlists)

title_query = solara.reactive("")
per_page = solara.reactive(10)
sort_by = solara.reactive("upload_date")
sort_order = solara.reactive("desc")

disabled_videos = solara.reactive(False)

num_pages = solara.reactive(0)
current_page = solara.reactive(1)

config = init_config()
WORKING = config["paths"]["working"]
STORAGE = config["paths"]["storage"]


@solara.component
def VideoDetail(video, router):
    with solara.Card(video.title):
        solara.Markdown(f"***This is the Detail Section for {video.title}!!!!***")

        if video.poster:
            img = Path(video.poster.path) / (
                video.poster.filename + video.poster.extension
            )
            solara.Image(img, width="400px")
        with solara.Column():

            solara.Markdown(f"**Sections**: {video.sections.count()}")
            solara.Markdown(f"**Files**: {video.files.count()}")

            solara.Markdown(f"**Duration**: {video.duration}")
            solara.Button("Refresh Video Info", on_click=lambda: video.update_from_yt())
            solara.Button(
                "Download Video File", on_click=lambda: video.download_video()
            )
            solara.Button("Extract Audio", on_click=lambda: video.extract_audio())

        solara.Markdown("## Files")
        for vf in video.files:
            with solara.Column():
                solara.Markdown(f"**File**: {vf.filename + vf.extension}")
        with solara.CardActions():

            solara.Button("Back to Videos", on_click=lambda: router.push("/videos"))


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        return
    video_id = router.parts[level:][0]
    if video_id.isdigit():
        vid = Video.get(id=video_id)
        if vid is None:
            solara.Markdown(f"Video with id {video_id} not found")
        else:
            VideoDetail(vid, router)
