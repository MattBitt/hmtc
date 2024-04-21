import solara
import solara.lab
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Channel, Playlist, ChannelVideo, Video
from loguru import logger


def update_channels():
    channels = Channel.select()
    for channel in channels:
        logger.debug("Checking for new videos in channel: {}", channel.name)
        channel.check_for_new_videos()


def output_missing_video_titles():
    channels = Channel.select().join(ChannelVideo).distinct()
    missing_vids = []
    for channel in channels:
        logger.debug("Checking for missing videos in channel: {}", channel.name)
        for vid in channel.channel_vids:
            v = Video.get_or_none(Video.youtube_id == vid.youtube_id)
            if not v:
                missing_vids.append(vid.youtube_id)
    with open("missing_vids.txt", "w") as f:
        for vid in missing_vids:
            f.write(f"{vid}\n")


@solara.component
def Page():

    MyAppBar()
    with solara.Column():
        solara.Markdown("## Channels")
        solara.Button("Update Channels", on_click=update_channels)
        solara.Button(
            "Output Missing Video Titles", on_click=output_missing_video_titles
        )

    for channel in Channel.select().join(Playlist).distinct():
        with solara.Card():

            solara.Markdown(f"### {channel.name}")
            solara.Markdown(f"**{channel.num_videos}** Videos on Channel")

            solara.Markdown("### My DB")
            total = 0
            for playlist in channel.playlists:
                cnt = playlist.videos.count()
                total += cnt
                solara.Markdown(f"**{cnt}** Videos in {playlist.name}")
            solara.Markdown(f"**{total}** Total Videos in DB")
            solara.Markdown(
                f"**{channel.num_videos - total} ({(channel.num_videos-total)/channel.num_videos*100:.0f}%) Videos Unanalyzed**"
            )
