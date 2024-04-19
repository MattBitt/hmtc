import math
import solara
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Video, Series, Playlist, PlaylistVideo, File, VideoFile
from loguru import logger
from dataclasses import dataclass
from hmtc.config import init_config

app_title = solara.reactive("HMTC - ")


# # all_series = [x.name for x in Series.select()]
series = solara.reactive([x for x in Series.select()])
# filters = solara.reactive(None)


# videos = solara.reactive(None)


# all_languages = "Python C++ Java JavaScript TypeScript BASIC".split()
# languages = solara.reactive([all_languages[0]])
# food = solara.reactive("Banana")
# foods = ["Kiwi", "Banana", "Apple"]


def get_video(video_id):

    query = (
        Video.select()
        .join(PlaylistVideo)
        .join(Playlist)
        .switch(Video)
        .join(Series)
        .switch(Video)
        .join(VideoFile)
        .join(File)
        .where(Video.id == video_id)
    )
    return query.get()


def get_videos(order_by=None, sort_direction=None):

    query = (
        Video.select(Video.id, Video.title)
        .join(PlaylistVideo)
        .join(Playlist)
        .switch(Video)
        .join(Series)
        .switch(Video)
        .join(VideoFile)
        .join(File)
        .where(VideoFile.file_type == "poster")
    )
    return query


def find_page(
    search,
):
    if not search:
        return 1
    else:
        return int(search.split("=")[1])


@dataclass
class VideoFilters:
    series: str


@solara.component
def VideoDetail(video_id):

    loading, set_loading = solara.use_state(True)
    video = solara.reactive(Video.get(Video.id == video_id))

    if loading is True:
        solara.Div("Loading...")
        video = Video.get(Video.id == video_id)
        set_loading(False)
    else:
        with solara.Column():
            solara.Markdown(video.value.title)
            if video.value.poster:
                with solara.Link(f"/videos/{video.value.id}"):
                    solara.Image(video.value.poster, width="300px")
            solara.Markdown(video.value.series.name)
            solara.Markdown(f"**Uploaded**: {video.value.upload_date}")
            with solara.Column():
                solara.Markdown("### Sections")
                for section in video.value.sections:
                    with solara.Row():
                        solara.Markdown(f"Start: {str(section.start)}")
                        solara.Markdown(f"End: {str(section.end)}")
                        solara.Markdown(f"Section Type: {section.section_type}")
            solara.Markdown(f"**Description**: {video.value.description}")


@solara.component
def VideoCard(video_id):
    loading, set_loading = solara.use_state(True)
    vid = Video.get(Video.id == video_id)
    if loading and vid is not None:
        solara.SpinnerSolara()
        set_loading(False)
    if not loading and vid is not None:
        with solara.Card():
            solara.Markdown(str(vid.id))
            if vid.title:
                solara.Markdown(vid.title)
            if vid.poster:
                with solara.Link(f"/videos/{vid.id}"):
                    solara.Image(vid.poster, width="100%")

            solara.Markdown(vid.series.name)
            solara.Markdown(f"**Uploaded**: {vid.upload_date}")


def calc_number_pages(number_videos, per_page):
    return math.ceil(number_videos / per_page)


@solara.component
def VideosGalleryComponent(init_query=None):
    config = init_config()
    # query parameters
    per_page = int(config.get("GENERAL", "PER_PAGE"))
    sort, set_sort = solara.use_state(None)
    filter, set_filter = solara.use_state("")
    query, set_query = solara.use_state(init_query)
    # query results
    number_videos, set_number_videos = solara.use_state(0)
    current_page, set_current_page = solara.use_state(1)
    number_pages, set_number_pages = solara.use_state(1)

    # actual query
    loading, set_loading = solara.use_state(True)
    video_ids, set_video_ids = solara.use_state(None)
    query = None

    def next_page():
        if query is not None:
            set_video_ids(query.paginate((int(current_page) + 1), per_page))
            set_current_page(current_page + 1)
            set_loading(True)
        else:
            logger.debug("No query but next page was clicked?")

    def prev_page():
        if query is None:
            return
        set_video_ids(query.paginate((int(current_page) - 1), per_page))

        set_current_page(current_page - 1)
        set_loading(True)

    # def order_by_date_desc():
    #     set_loading(True)
    #     set_sort("desc")
    #     set_current_page(1)
    #     set_number_pages(calc_number_pages(number_videos, per_page))
    #     set_video_ids(
    #         get_videos(order_by="date", sort_direction=sort)
    #         .order_by(Video.upload_date.desc())
    #         .paginate((int(current_page)), per_page)
    #     )

    #     set_loading(False)

    # def order_by_date_asc():
    #     set_loading(True)
    #     set_current_page(1)
    #     query = get_videos(order_by="date", sort_direction="asc")
    #     if filter:
    #         query = query.where(Video.title.contains(filter))
    #     set_number_videos(query.count())
    #     set_video_ids((query.order_by(Video.upload_date.asc())))

    def search():
        # logger.debug("Reloading...")
        # set_loading(True)
        set_current_page(1)
        query = get_videos().where(Video.title.contains(filter))
        set_number_videos(query.count())
        set_number_pages(
            calc_number_pages(query.count(), int(config.get("GENERAL", "PER_PAGE")))
        )
        set_video_ids(
            (query.order_by(Video.upload_date.asc())).paginate(
                (int(current_page)), int(config.get("GENERAL", "PER_PAGE"))
            )
        )
        set_loading(False)

    if loading:
        logger.debug(f"Loading, filter = {filter}")
        if query is None:
            logger.debug("theres no query here..")
            # query = get_videos()
        else:
            if filter:
                set_query(query.where(Video.title.contains(filter)))
            set_number_videos(query.count())
            set_number_pages(
                calc_number_pages(number_videos, int(config.get("GENERAL", "PER_PAGE")))
            )
            set_video_ids(
                query.paginate(
                    (int(current_page)), int(config.get("GENERAL", "PER_PAGE"))
                )
            )

            set_loading(False)

    else:
        if number_videos == 0:

            solara.Markdown("No videos found")
        else:
            with solara.Row(justify="space-between"):

                solara.Markdown(f"## Page {str(current_page)} of {number_pages} ")
                solara.Markdown(f"(Sort: {sort if sort else ''}) (Filter: {filter} )")
                solara.Markdown(f"## {number_videos} videos found")
                solara.Div(
                    [
                        solara.InputText(
                            label="Search",
                            value=filter,
                            on_value=set_filter,
                            continuous_update=True,
                        ),
                        solara.Button("Search", on_click=search),
                        # solara.Button(
                        #     "Sort Descending by date", on_click=order_by_date_desc
                        # ),
                        # solara.Button(
                        #     "Sort Ascending by date", on_click=order_by_date_asc
                        # ),
                        solara.Button(
                            "Previous", on_click=prev_page, disabled=(current_page == 1)
                        ),
                        solara.Button(
                            "Next",
                            on_click=next_page,
                            disabled=(current_page == number_pages),
                        ),
                    ]
                )

            with solara.ColumnsResponsive(12, large=[4, 4, 4]):
                for video in video_ids:
                    VideoCard(video.id)


@solara.component
def VideoDetailCard(video_id):
    video = solara.use_reactive(Video.get(Video.id == video_id))

    if video.value is not None:
        vid = video.value
        with solara.Card(title=vid.title):

            solara.Markdown(vid.title)
            # solara.Image(Path(vid.poster), width=f"300px")

            solara.Markdown(vid.series.name)
            solara.Markdown(f"**Uploaded**: {vid.upload_date}")
            with solara.CardActions():

                with solara.Link(f"/videos/{vid.id}"):
                    solara.Button("Edit")

                solara.Button("Delete")
    else:
        solara.Markdown("No video found")


@solara.component
def VideosView():
    query = (
        Video.select()
        .join(PlaylistVideo)
        .join(Playlist)
        .switch(Video)
        .join(Series)
        .order_by("upload_date")
        # .limit(15)
    )

    query = query.where(
        Video.series.in_(
            Series.select().where(Series.name.in_([n.name for n in series.value]))
        )
    )
    videos.set([x for x in query])
    with solara.ColumnsResponsive(12, large=[4, 4, 4]):
        solara.Markdown(f"## Videos ({query.count()} found)")
        for vid in query.limit(15):
            # solara.Markdown(f"# {vid.title}")
            VideoDetailCard(vid.id)
    solara.Markdown("The end...")


@solara.component
def SeriesFilter():
    series = solara.use_reactive(Series.select())
    selected = solara.use_reactive([s for s in series.value])

    with solara.Card("Series"):
        solara.Markdown("## Help!")
        # solara.ToggleButtonsMultiple(selected.value, series, dense=True)
        for s in series.value:
            with solara.ToggleButtonsSingle(value=selected):
                solara.Button(
                    s.name,
                    icon_name="mdi-arrow-up-bold",
                    value=(selected.value),
                    text=True,
                )
        solara.Markdown(f"**Selected**: {selected.value}")


@solara.component
def Filters(series_filter):

    with solara.Card("Filters"):

        SeriesFilter()
        with solara.CardActions():
            solara.Button("Apply Filters")
            solara.Button("Clear Filters")


@solara.component
def Search():
    search_text = solara.use_reactive("")
    with solara.Card("Search"):
        with solara.Row():
            solara.InputText("Search", value=search_text)
            solara.Button(
                "Search", on_click=lambda: logger.debug(f"Searching... {search_text}")
            )


@solara.component
def Sort():
    with solara.Card("Sort"):
        solara.Button("Sort by Date")
        solara.Button("Sort by Title")


@solara.component
def VideosToolBar(series_filter):

    with solara.Columns():
        with solara.Row():
            # Filters(series_filter)
            Search()
            Sort()


@solara.component
def ToggleButton(value, on_click, text=False):
    with solara.Button(on_click=on_click):
        if text:
            solara.Markdown(value)
        else:
            solara.Icon(value)


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()
    # selected_series = solara.use_reactive(Series.select())

    MyAppBar()

    def apply():
        logger.debug("Applying")

    def toggle(id):
        logger.debug("Toggling")

    if router.parts[-1] == "videos":
        solara.Markdown("## Videos View will go here")

    else:

        video_id = router.parts[level:][0]
        if video_id.isdigit():
            VideoDetail(get_video(video_id))
        else:
            solara.Markdown(f"Video Id not understood {video_id}")
