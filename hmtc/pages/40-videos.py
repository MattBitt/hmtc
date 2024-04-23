import solara
from hmtc.models import Series, Video, Playlist, PlaylistVideo
from hmtc.components.multi_select import MultiSelect
from hmtc.components.single_select import SingleSelect
from pathlib import Path
from hmtc.config import init_config

config = init_config()

all_languages = "Python C++ Java JavaScript TypeScript BASIC".split()
languages = solara.reactive([all_languages[0]])

all_series = [s.name for s in Series.select()]
selected_series = solara.reactive(all_series)


all_playlists = [p.name for p in Playlist.select()]
selected_playlist = solara.reactive(all_playlists)

title_query = solara.reactive("")
per_page = solara.reactive(10)
sort_by = solara.reactive("upload_date")
sort_order = solara.reactive("desc")

disabled_videos = solara.reactive(False)

num_pages = solara.reactive(0)
current_page = solara.reactive(1)


@solara.component
def VideoCard(video):
    with solara.Card(video.title):
        solara.Markdown(f"## Video ID {video.id}")
        with solara.Row():
            solara.Markdown(f"**Sections**: {video.sections.count()}")
            solara.Markdown(f"**Files**: {video.files.count()}")
            solara.Markdown(f"**Duration**: {video.duration}")
        with solara.CardActions():
            with solara.Link(f"/videos/{video.id}"):
                solara.Button("Edit")
            solara.Button("Delete")


@solara.component
def SortToolBar():
    with solara.Card("Sorting"):
        with solara.Row(justify="space-between"):
            SingleSelect("Sort By", sort_by, ["upload_date", "title"])
            SingleSelect("Sort Order", sort_order, ["asc", "desc"])


@solara.component
def PaginationControls():
    with solara.Card("Pagination"):

        solara.Button(
            "First",
            on_click=lambda: current_page.set(1),
            disabled=(current_page.value == 1),
        )
        solara.Button(
            "Previous",
            on_click=lambda: current_page.set(current_page.value - 1),
            disabled=(current_page.value == 1),
        ),

        solara.Button(
            "Next",
            on_click=lambda: current_page.set(current_page.value + 1),
            disabled=(current_page.value == num_pages.value),
        )
        solara.Button(
            "Last",
            on_click=lambda: current_page.set(num_pages.value),
            disabled=(current_page.value == num_pages.value),
        )
        SingleSelect("Videos per page", per_page, [5, 10, 20, 50, 100])
        solara.Markdown(f"Page {current_page.value} of {num_pages.value}")


@solara.component
def SeriesFilterCard():
    with solara.Card(title="Series"):
        MultiSelect("Series", selected_series, all_series)
        with solara.CardActions():
            solara.Button("Clear", on_click=lambda: selected_series.set([]))
            solara.Button(
                "Select All", on_click=lambda: selected_series.set(all_series)
            )


@solara.component
def PlaylistFilterCard():
    with solara.Card(title="Playlists"):
        MultiSelect("Playlist", selected_playlist, all_playlists)
        with solara.CardActions():
            solara.Button("Clear", on_click=lambda: selected_playlist.set([]))
            solara.Button(
                "Select All", on_click=lambda: selected_playlist.set(all_playlists)
            )


@solara.component
def ShowDisabledVideos():
    with solara.Card():
        solara.Checkbox(label="Show Disabled Videos", value=disabled_videos)


@solara.component
def TitleTextFilter():
    with solara.Card():
        solara.InputText(
            "Search Video Titles", value=title_query, continuous_update=True
        )


def get_sort_method():
    sort_mapping = {
        ("upload_date", "asc"): Video.upload_date.asc(),
        ("upload_date", "desc"): Video.upload_date.desc(),
        ("title", "asc"): Video.title.asc(),
        ("title", "desc"): Video.title.desc(),
    }
    if sort_by.value not in ["upload_date", "title"]:
        sort_by.set("upload_date")
    if sort_order.value not in ["asc", "desc"]:
        sort_order.set("desc")

    return sort_mapping.get((sort_by.value, sort_order.value))


@solara.component
def VideoDetail(video, router):
    with solara.Card(video.title):
        solara.Markdown(f"***This is the Detail Section for {video.title}!!!!***")
        path = config.get("MEDIA", "VIDEO_PATH")
        if video.poster:
            solara.Image(f"{Path(path) / video.poster}", width="200px")
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
                solara.Markdown(f"**File**: {vf.file.filename}")
        with solara.CardActions():

            solara.Button("Back to Videos", on_click=lambda: router.push("/videos"))


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()

    if router.parts[-1] == "videos":
        # this sql will return all videos that have more than 1 section
        # SELECT video.*, (SELECT COUNT(*) FROM section WHERE section.video_id = video.id) AS TOT FROM video where TOT > 1;
        SeriesFilterCard()
        PlaylistFilterCard()
        ShowDisabledVideos()
        with solara.ColumnsResponsive(12, large=4):

            TitleTextFilter()
            SortToolBar()

        query = (
            Video.select()
            .join(PlaylistVideo)
            .join(Playlist)
            .join(Series)
            .switch(Video)
            .where(Series.name.in_(selected_series.value))
            .where(
                (Playlist.name.in_(selected_playlist.value))
                & (Playlist.series == Series.id)
            )
        )

        if not disabled_videos.value:
            query = query.where(Video.enabled == True)

        if title_query.value:
            query = query.where(Video.title.contains(title_query.value))

        solara.Markdown(f"## Total: {query.count()} videos found.")

        query = query.order_by(get_sort_method())

        num_pages.set(query.count() // per_page.value + 1)
        if current_page.value > num_pages.value:
            current_page.set(1)
        with solara.ColumnsResponsive(12, large=4):
            for video in query.paginate(current_page.value, per_page.value):
                VideoCard(video)

        PaginationControls()

    else:

        video_id = router.parts[level:][0]
        if video_id.isdigit():
            vid = Video.get(id=video_id)
            if vid is None:
                solara.Markdown(f"Video with id {video_id} not found")
            else:
                VideoDetail(vid, router)
        else:
            solara.Markdown(f"Video Id not understood {video_id}")
