import math
import solara
import pandas as pd
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Video, Series, Playlist, PlaylistVideo, File, VideoFile
from pathlib import Path
from loguru import logger
from peewee import JOIN
from dataclasses import dataclass
import time
from hmtc.config import init_config

app_title = solara.reactive("HMTC - ")


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
    upload_date: tuple[str, str]
    series: str
    title: str


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
    if loading and not vid is None:
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
def VideosView(videos):
    for vid in videos:
        solara.Markdown(f"{vid.id} - {vid.title}")


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()
    videos = solara.use_reactive(None)

    MyAppBar()
    solara.Markdown(f"## {videos.value}")
    solara.Button("Update Videos", on_click=lambda: videos.set(get_videos()))
    if router.parts[-1] == "videos":
        if videos.value is not None:
            VideosView(videos.value)
        else:
            solara.Text("No videos found")

    else:
        video_id = router.parts[level:][0]
        VideoDetail(get_video(video_id))
