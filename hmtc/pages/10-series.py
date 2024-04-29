import solara
import solara.lab
from loguru import logger
from hmtc.models import Video, Series, VideoFile, File
from hmtc.components.progress_slider import SimpleProgressBar
import time
import peewee

name = solara.reactive("")
start_date = solara.reactive("2001-01-01")
end_date = solara.reactive("2024-12-31")


def videos_by_series(series):
    return Video.select().where((Video.series == series) & (Video.enabled == True))


def add_series():
    logger.debug("About to add series")
    try:
        Series.create(name="New Series", start_date="2021-01-01", end_date="2024-12-31")
    except peewee.IntegrityError:
        logger.error("Series already exists")
        return


@solara.component
def SeriesForm():
    with solara.Card():
        solara.InputText("Series Name", value=name)
        solara.InputText("Series Start Date", value=start_date)
        solara.InputText("Series End Date", value=end_date)
        solara.Button("Submit", on_click=add_series)


@solara.component
def SeriesCard(series):
    def download_missing_videos():
        videos = videos_by_series(series)

        for video in videos:
            if not video.has_video:
                video.download_video()
                time.sleep(10)

    def extract_audio():
        videos = videos_by_series(series)

        for video in videos:
            if video.has_video and not video.has_audio:
                video.extract_audio()
                time.sleep(1)

    def refresh_info(ser):
        videos = videos_by_series(ser)

        for video in videos:

            video.update_from_yt()

        logger.success(f"Refreshed video info for series: {ser.name}")

    vids_with_video = (
        Video.select()
        .join(VideoFile)
        .join(File)
        .switch(Video)
        .where((Video.series == series) & (VideoFile.file_type == "video"))
    )

    if vids_with_video.count() == 0:
        logger.warning(f"No videos with video files for series {series.name}")
        logger.warning(f"Not checking further info for series {series.name}")
        SeriesForm()
        return

    vids_with_audio = (
        Video.select()
        .join(VideoFile)
        .join(File)
        .switch(Video)
        .where((Video.series == series) & (VideoFile.file_type == "audio"))
    )
    vids_with_image = (
        Video.select()
        .join(VideoFile)
        .join(File)
        .switch(Video)
        .where(
            (Video.enabled == True)
            & (Video.series == series)
            & (VideoFile.file_type == "image")
        )
        .distinct()
    )
    vids_with_subtitle = (
        Video.select()
        .join(VideoFile)
        .join(File)
        .switch(Video)
        .where(
            (Video.enabled == True)
            & (Video.series == series)
            & (VideoFile.file_type == "subtitle")
        )
        .distinct()
    )

    total_time = [v.duration for v in vids_with_video if v.duration is not None]

    with solara.Card():

        solara.Markdown(f"# {series.name}")
        solara.Markdown(f"* **{series.enabled_videos}** (enabled) sources")
        solara.Markdown(
            f"* **{series.total_videos - series.enabled_videos }** (disabled)"
        )
        solara.Markdown("##Files for this Series")

        solara.Markdown(
            f"Total playing time of videos: {(sum(total_time)/ 3600):.0f} hours"
        )
        SimpleProgressBar(
            label="Videos with an audio file",
            current_value=vids_with_audio.count(),
            total=series.enabled_videos,
        )
        SimpleProgressBar(
            label="Videos with images",
            current_value=vids_with_image.count(),
            total=series.enabled_videos,
        )
        SimpleProgressBar(
            label="Videos with a video file",
            current_value=vids_with_video.count(),
            total=series.enabled_videos,
        )
        SimpleProgressBar(
            label="Videos with a subtitle file",
            current_value=vids_with_subtitle.count(),
            total=series.enabled_videos,
        )
        # solara.Markdown(
        #     f"**{vids_with_audio.count() / series.enabled_videos:.2%}** videos have an 'audio' file"
        # )
        # solara.Markdown(
        #     f"**{vids_with_image.count() / series.enabled_videos:.2%}** videos have an 'image' file"
        # )
        # solara.Markdown(
        #     f"**{vids_with_video.count() / series.enabled_videos:.2%}** videos have an 'audio' file"
        # )
        solara.Button(
            "Refresh Video Info",
            on_click=lambda: refresh_info(series),
        )

        solara.Button(
            "Download Missing Videos",
            on_click=download_missing_videos,
        ),
        solara.Button(
            "Extract Audio Files",
            on_click=extract_audio,
        )


@solara.component
def Page():
    solara.Button("Add Series", on_click=add_series)
    with solara.ColumnsResponsive(12, large=4):

        series = Series.select()
        for ser in series:
            SeriesCard(ser)
