import solara
import solara.lab

from hmtc.models import Video, Series, VideoFile, File
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
    total_time = [v.duration for v in vids_with_video if v.duration is not None]
    with solara.Card():

        solara.Markdown(f"# {series.name}")
        solara.Markdown(f"**{series.enabled_videos}** (enabled) sources")
        solara.Markdown(
            f"**{series.total_videos - series.enabled_videos }** (disabled)"
        )
        solara.Markdown("##Video Files")
        solara.Markdown(
            f"**{vids_with_video.count()}** videos have a 'video' file ({vids_with_video.count() / series.enabled_videos:.2%})"
        )
        solara.Markdown(
            f"Total playing time of videos: {(sum(total_time)/ 3600):.0f} hours"
        )
        solara.Markdown(f"**{vids_with_audio.count()}** videos have an 'audio' file")
        solara.Markdown(f"**{vids_with_image.count()}** videos have an 'image' file")
        solara.Button(
            "Download Missing Videos",
            on_click=download_missing_videos,
        )


@solara.component
def Page():
    with solara.ColumnsResponsive(12, large=4):

        series = Series.select()
        for ser in series:
            SeriesCard(ser)
