import solara
import solara.lab

from hmtc.models import Video, Series, VideoFile, File
from hmtc.components.progress_slider import SimpleProgressBar
import time


@solara.component
def SeriesCard(series):
    def download_missing_videos():
        videos = Video.select().where(
            (Video.enabled == True) & (Video.series == series)
        )
        for video in videos:
            if not video.has_video:
                video.download_video()
                time.sleep(10)

    def extract_audio():
        videos = Video.select().where(
            (Video.enabled == True) & (Video.series == series)
        )
        for video in videos:
            if video.has_video and not video.has_audio:
                video.extract_audio()
                time.sleep(1)

    def refresh_info():
        videos = Video.select().where(
            (Video.enabled == True) & (Video.series == series)
        )
        for video in videos:
            video.download_video_info(video.youtube_id)

    vids_with_video = (
        Video.select()
        .join(VideoFile)
        .join(File)
        .switch(Video)
        .where((Video.series == series) & (VideoFile.file_type == "video"))
    )
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
            value=vids_with_audio.count() / series.enabled_videos * 100,
        )
        SimpleProgressBar(
            label="Videos with images",
            value=vids_with_image.count() / series.enabled_videos * 100,
        )
        SimpleProgressBar(
            label="Videos with a video file",
            value=vids_with_video.count() / series.enabled_videos * 100,
        )
        SimpleProgressBar(
            label="Videos with a subtitle file",
            value=vids_with_subtitle.count() / series.enabled_videos * 100,
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
            on_click=refresh_info,
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
    with solara.ColumnsResponsive(12, large=4):

        series = Series.select()
        for ser in series:
            SeriesCard(ser)
