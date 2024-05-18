from pathlib import Path

import peewee
import solara
import solara.lab
from loguru import logger

from hmtc.components.file_drop_card import FileDropCard, FileInfo
from hmtc.config import init_config
from hmtc.models import Channel

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


def ChannelDetail(channel_id, uploaded_new_file):
    filename = solara.use_reactive("")
    size, set_size = solara.use_state(0)

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
            solara.Markdown(f"Poster: {channel.poster.filename}")
            solara.Image(image=channel.poster, width="50%")

        FileDropCard(on_file=import_file)
        solara.Checkbox(label="Enabled", value=enabled)

        with solara.CardActions():
            solara.Button(label="Save", on_click=update_channel)


@solara.component
def Page():
    with solara.ColumnsResponsive(12, large=6):
        with solara.Card():
            solara.Markdown("old stuff1)")
    # def update_my_videos():
    #     for channel in Channel.select():
    #         channel.update_videos_with_channel_info()

    # with solara.ColumnsResponsive(
    #     12,
    #     large=6,
    # ):
    #     for channel in Channel.select().order_by(Channel.updated_at.desc()):
    #         ChannelCard(channel)
    # solara.Button("Add New Channel", on_click=add_new_channel)
    # solara.Button(
    #     "Update all Videos with properties of their respective channels",
    #     on_click=update_my_videos,
    # )
