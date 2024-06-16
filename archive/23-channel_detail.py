from pathlib import Path

import peewee
import solara
import solara.lab
from loguru import logger
from solara.lab import task

from hmtc.components.file_drop_card import FileDropCard, FileInfo
from hmtc.config import init_config
from hmtc.models import Channel
from hmtc.utils.general import time_since_update

all_channels = [c.name for c in Channel.select()]
if all_channels == []:
    all_channels = ["No Channels"]

name = solara.reactive("")
url = solara.reactive("http://www.youtube.com")
enabled = solara.reactive(True)
last_update_completed = solara.reactive(None)

config = init_config()

UPLOAD_PATH = Path(config["paths"]["working"]) / "uploads"


def update_channels():
    channels = Channel.select()
    for channel in channels:
        logger.debug("Checking for new videos in channel: {}", channel.name)
        channel.check_for_new_videos()


# def output_missing_video_titles():
#     channels = Channel.select().join(ChannelVideo).distinct()
#     missing_vids = []
#     for channel in channels:
#         logger.debug("Checking for missing videos in channel: {}", channel.name)
#         for vid in channel.channel_vids:
#             v = Video.get_or_none(Video.youtube_id == vid.youtube_id)
#             if not v:
#                 missing_vids.append(vid.youtube_id)
#     with open("missing_vids.txt", "w") as f:
#         for vid in missing_vids:
#             f.write(f"{vid}\n")


def update_all():
    logger.debug("Updating")
    for p in Channel.select().where(Channel.enabled == True):
        p.check_for_new_videos()
    logger.success("Updated all channels")


def add_new_channel():
    try:
        channel = Channel.create(
            name="New Channel",
            url="http://www.youtube.com",
            youtube_id="adsuoibgvpfrjdlk;af",
            enabled=True,
            last_update_completed=None,
        )

        logger.debug(f"Created new channel: {channel.name}")
    except peewee.IntegrityError:
        logger.debug("Channel already exists")
        return


def save_channel(channel):
    channel.name = name.value
    channel.url = url.value
    channel.enabled = True
    channel.save()
    logger.success(f"Added new channel {channel.name}")


def write_to_disk(file: FileInfo):
    logger.debug(f"Writing file to disk: {file['name']}")

    with open(UPLOAD_PATH / file["name"], "wb") as src_file:
        src_file.write(file["data"])

    return file["name"]


def ChannelDetail(channel_id):
    channel = Channel.select().where(Channel.id == channel_id).get()
    name.set(channel.name)
    url.set(channel.url)
    enabled.set(channel.enabled)
    last_update_completed.set(channel.last_update_completed)

    def import_file(file: FileInfo):
        filename = write_to_disk(file)
        logger.debug(f"Importing file {filename} to channel {channel.name}")

        f = channel.add_file(UPLOAD_PATH / filename)

        return f

    def update_channel():
        save_channel(channel)
        logger.success(f"Updated channel {channel.name}")

    with solara.Card():
        solara.InputText(label="Name", value=name, continuous_update=False)
        solara.InputText(label="URL", value=url, continuous_update=False)
        if channel and channel.poster:
            solara.Markdown(f"Poster: {channel.poster}")
            solara.Image(image=channel.poster, width="300px")

        FileDropCard(on_file=import_file)
        solara.Checkbox(label="Enabled", value=enabled)

        with solara.CardActions():
            solara.Button(label="Save", on_click=update_channel)


@solara.component
def ChannelCard(channel):
    updating = solara.use_reactive(False)

    def update_playlists():
        logger.debug(f"Updating channel {channel.name}")
        updating.set(True)
        channel.check_for_new_playlists()
        updating.set(False)
        logger.success(f"Updated database from Channel {channel.name}")

    @task
    def update():
        logger.debug(f"Updating channel {channel.name}")
        updating.set(True)
        channel.check_for_new_videos()
        updating.set(False)
        logger.success(f"Updated database from Channel {channel.name}")

    with solara.Column():
        with solara.Card():
            if updating.value is False:
                solara.Markdown(channel.name)
                if channel.poster is not None:
                    solara.Image(channel.poster, width="300px")
                solara.Markdown(f"URL: {channel.url}")
                solara.Markdown(f"Last Updated: {time_since_update(channel)}")
                solara.Markdown(f"Enabled: {channel.enabled}")
                with solara.CardActions():
                    with solara.Link(f"/channels/{channel.id}"):
                        solara.Button("Edit", on_click=lambda: logger.debug("Edit"))
                    solara.Button("Delete", on_click=lambda: channel.delete_instance())
                    solara.Button(label="Check for new Videos", on_click=update)
                    solara.Button(
                        label="Check for new Playlists", on_click=update_playlists
                    )
            else:
                solara.SpinnerSolara()
            solara.Markdown(f"### {channel.name}")
            solara.Markdown(f"**{channel.videos.count()}** Videos on Channel")

            with solara.Column():
                for f in channel.files:
                    solara.Markdown(f"{f.filename}")


@solara.component
def Page():
    def update_my_videos():
        for channel in Channel.select():
            channel.update_videos_with_channel_info()

    with solara.ColumnsResponsive(
        12,
        large=3,
    ):
        for channel in Channel.select().order_by(Channel.updated_at.desc()):
            ChannelCard(channel)
    solara.Button("Add New Channel", on_click=add_new_channel)
    solara.Button(
        "Update all Videos with properties of their respective channels",
        on_click=update_my_videos,
    )


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Channel Selected")
        return
    channel_id = router.parts[level:][0]
    if channel_id.isdigit():
        ChannelDetail(channel_id)
