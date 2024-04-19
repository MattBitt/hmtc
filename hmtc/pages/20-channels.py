import solara
import solara.lab
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Channel, Playlist
from loguru import logger


def update_channels():
    channels = Channel.select()
    for channel in channels:
        logger.debug("Checking for new videos in channel: {}", channel.name)
        channel.check_for_new_videos()


@solara.component
def Page():

    MyAppBar()
    with solara.Column():
        solara.Markdown("## Channels")
        solara.Button("Update Channels", on_click=update_channels)

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
