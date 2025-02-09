import solara
from loguru import logger

from hmtc.components.sectionalizer.main import VideoFrame
from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.domains.album import Album
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel
from hmtc.utils.general import paginate

refresh_counter = solara.reactive(1)


@solara.component
def SecondRow(
    video: Video,
):
    error = solara.use_reactive("")
    success = solara.use_reactive("")
    unique = solara.use_reactive(video.instance.unique_content)

    def assign_album(title):
        album = Album.get_by(title=title)
        if album is None:
            error.set(f"Album Not Found")
            return
        album.add_video(video.instance)
        success.set(f"{video.instance.title} added to {album.instance.title}")
        refresh_counter.set(refresh_counter.value + 1)

    def toggle_unique():
        new_unique = not video.instance.unique_content
        video.instance.unique_content = new_unique
        video.instance.save()
        unique.set(new_unique)
        refresh_counter.set(refresh_counter.value + 1)

    def delete_video_file():
        logger.error(f"Deleting video_file for {video.instance.title}")
        video.delete_file("video")
        refresh_counter.set(refresh_counter.value + 1)

    with solara.Columns([8, 4]):
        with solara.Card("Album"):
            with solara.ColumnsResponsive():
                solara.Button(
                    "Energy Exchange Tour",
                    on_click=lambda: assign_album("Energy Exchange Tour"),
                    classes=["button"],
                )
                solara.Button(
                    "Happy Hour",
                    on_click=lambda: assign_album("Happy Hour"),
                    classes=["button"],
                )
                solara.Button(
                    "Interviews",
                    on_click=lambda: assign_album("Interviews"),
                    classes=["button"],
                )
                solara.Button(
                    "Livestream Highlights",
                    on_click=lambda: assign_album("Livestream Highlights"),
                    classes=["button"],
                )
                solara.Button(
                    "No Where Else to Put These",
                    on_click=lambda: assign_album("No Where Else to Put These"),
                    classes=["button"],
                )
                solara.Button(
                    "Odyssey Tour",
                    on_click=lambda: assign_album("Odyssey Tour"),
                    classes=["button"],
                )
                solara.Button(
                    "On the Street",
                    on_click=lambda: assign_album("On the Street"),
                    classes=["button"],
                )
            with solara.Row():
                if error.value != "":
                    solara.Error(error.value)
                    solara.Button(
                        f"Clear", on_click=lambda: error.set(""), classes=["button"]
                    )
                elif success.value != "":
                    solara.Success(success.value)
                    solara.Button(
                        f"Clear", on_click=lambda: success.set(""), classes=["button"]
                    )
        with solara.Card("Other"):

            with solara.ColumnsResponsive():
                solara.Button(
                    f"Unique: {str(unique.value)}",
                    on_click=toggle_unique,
                    classes=["button"],
                )
                solara.Button(
                    f"Delete Video File",
                    icon_name="mdi-delete",
                    on_click=delete_video_file,
                    classes=["button mywarning"],
                    disabled=video.video_file() is None,
                )


@solara.component
def MainRow(video: Video):
    if video.instance is None:
        with solara.Row(justify="center"):
            solara.Error("Instance is None...")
            return
    with solara.Card():
        with solara.Columns([6, 6]):
            with solara.Column():
                solara.Image(video.poster(), width="400px")

            with solara.Column():
                if video.video_file() is not None:
                    midpoint_ms = (video.instance.duration / 2) * 1000
                    VideoFrame(video=video, time_cursor=midpoint_ms)
                else:
                    solara.Warning(f"No Video File downloaded for this")
        with solara.Row(justify="center"):
            solara.Text(f"{video.instance.title}")


@solara.component
def VideoEditor():
    current_page = solara.use_reactive(1)
    vids_with_album = DiscVideoModel.select(DiscVideoModel.video_id).distinct()
    page_query = VideoModel.select(VideoModel).where(
        (VideoModel.id.not_in(vids_with_album) & (VideoModel.unique_content == False))
    )

    if len(page_query) == 0:
        solara.Warning(f"No Videos Found meeting these criteria.")
        return

    _query, num_items, num_pages = paginate(
        query=page_query,
        page=current_page.value,
        per_page=1,
    )

    if current_page.value > num_pages:
        current_page.set(num_pages)

    video = Video(_query.first())

    with solara.Row(justify="center"):
        MainRow(video)
    with solara.Row(justify="center"):
        SecondRow(video)
    with solara.Row(justify="center"):
        PaginationControls(
            current_page=current_page, num_pages=num_pages, num_items=num_items
        )


@solara.component
def Page():

    with solara.Column(classes=["main-container"]):
        # if refresh_counter.value > 0:
        VideoEditor()
