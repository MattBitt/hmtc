import solara
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.channel import ChannelItem
from hmtc.schemas.video import VideoItem

status = solara.reactive("Waiting for video URL")

video_url = solara.reactive("")

channel_name = solara.reactive("")
channel_url = solara.reactive("")
channel_auto_update = solara.reactive(False)
channel_youtube_id = solara.reactive("")

video_title = solara.reactive("")
video_description = solara.reactive("")
video_duration = solara.reactive("")
video_upload_date = solara.reactive("")


def add_video():
    url = video_url.value
    id = None
    if url == "":
        logger.debug("No video URL provided")
        status.set("No video URL provided")
        return

    if len(url) == 11:
        # this is a YouTube video ID
        url = id

    if url.startswith("http"):
        id = url.split("v=")[1]

    logger.error(f"Adding video ID: {id}")

    existing = VideoItem.get_by_youtube_id(id)
    if existing:
        logger.error(f"Video already exists in DB: {existing}")
        status.set("Video already exists in DB")
        return

    vid_info = VideoItem.grab_info_from_youtube(id)
    channel_id = vid_info["channel_id"]
    channel = ChannelItem.grab_by_youtube_id(channel_id)

    if not channel:
        logger.debug(f"Channel not found in DB. Using downloaded info.{channel_id}")
        status.set(
            f"Channel not found in DB. Using downloaded info. Add channel to DB before adding the video."
        )
        channel_name.set(vid_info["channel"])
        channel_url.set(vid_info["uploader_url"])
        channel_youtube_id.set(channel_id)
        channel_auto_update.set(False)

    else:
        logger.debug(f"Channel was found in DB. Loading info.")
        channel_name.set(channel.name)
        channel_url.set(channel.url)
        channel_youtube_id.set(channel.youtube_id)
        # need to store in the db
        channel_auto_update.set(False)

    video_title.set(vid_info["title"])
    video_description.set(vid_info["description"])
    video_duration.set(vid_info["duration"])
    video_upload_date.set(vid_info["upload_date"])

    # if not, grab initial info from youtube
    # need to create channel if it doesn't exist
    # then add the new videoitem to the db

    # VideoItem.create_from_youtube_id(id)


@solara.component
def AddNewVideo():
    solara.Markdown("## Add A New Video")
    with solara.Card():
        solara.InputText(
            "Enter a URL or YouTube Video ID",
            value=video_url,
            continuous_update=False,
        )
        solara.Button("Add Video", on_click=add_video, classes=["button"])
        solara.Markdown("## Status")
        solara.Markdown(f"## {status.value}")


@solara.component
def ChannelInfo():
    with solara.Card():
        solara.Markdown("## Channel Info")
        solara.InputText(
            "Channel Name",
            value=channel_name,
            continuous_update=False,
        )
        solara.InputText(
            "Channel URL",
            value=channel_url,
            continuous_update=False,
        )
        solara.InputText(
            "Channel YouTube ID",
            value=channel_youtube_id,
            continuous_update=False,
        )
        solara.Button(
            "Add Channel",
            classes=["button"],
            disabled=False,
            on_click=add_channel,
        )


@solara.component
def VideoInfo():
    # if this is shown, the channel should already exist and be in the db
    #

    # thumbnail image here
    with solara.Card():
        solara.Markdown("## Video Info")
        solara.InputText("Title", value=video_title)
        solara.InputText("Description", value=video_description)
        solara.InputText("Duration", value=video_duration)
        solara.InputText("Upload Date", value=video_upload_date)
        solara.Button(
            "Add Video",
            classes=["button"],
            disabled=False,
            on_click=add_video_to_db,
        )
        solara.Markdown(f"#### Channel: {channel_name.value}")


def add_channel():
    logger.error("Adding a new channel")
    new_item = ChannelItem(
        name=channel_name.value,
        enabled=True,
        youtube_id=channel_youtube_id.value,
        url=channel_url.value,
    )
    new_item.save_to_db()


def add_video_to_db():
    logger.debug("Adding video to db")

    VideoItem.create_from_youtube_id(video_url.value.split("v=")[1])


@solara.component
def Page():

    MySidebar(solara.use_router())

    with solara.Column(classes=["main-container"]):
        with solara.Column():

            AddNewVideo()
            ChannelInfo()
            VideoInfo()
