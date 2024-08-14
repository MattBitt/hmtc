import solara
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.channel import ChannelItem
from hmtc.schemas.video import VideoItem

video_url = solara.reactive("")

channel_name = solara.reactive("")
channel_url = solara.reactive("")
channel_auto_update = solara.reactive(False)
new_channel = solara.reactive(False)


video_title = solara.reactive("")
video_description = solara.reactive("")
video_duration = solara.reactive("")
video_upload_date = solara.reactive("")


def add_video():
    url = video_url.value
    id = None
    if url == "":
        logger.debug("No video URL provided")
        return "No video URL provided"

    if len(url) == 11:
        # this is a YouTube video ID
        url = id

    if url.startswith("http"):
        id = url.split("v=")[1]

    logger.error(f"Adding video ID: {id}")

    existing = VideoItem.get_by_youtube_id(id)
    if existing:
        logger.error(f"Video already exists in DB: {existing}")
        return "Video already exists in DB"

    vid_info = VideoItem.grab_info_from_youtube(id)
    channel_id = vid_info["channel_id"]
    channel = ChannelItem.grab_by_youtube_id(channel_id)

    if not channel:
        logger.error(f"Channel not found in DB: {channel_id}")

        channel_name.set(vid_info["channel"])
        channel_url.set(vid_info["channel_url"])
        channel_auto_update.set(False)
        new_channel.set(True)
        # return "Channel not found in DB, need to add."
    else:
        channel_name.set(channel.name)
        channel_url.set(channel.url)

        # need to store in the db
        channel_auto_update.set(False)

        new_channel.set(False)

    video_title.set(vid_info["title"])
    video_description.set(vid_info["description"])
    video_duration.set(vid_info["duration"])
    video_upload_date.set(vid_info["upload_date"])

    # if not, grab initial info from youtube
    # need to create channel if it doesn't exist
    # then add the new videoitem to the db

    # VideoItem.create_from_youtube_id(id)


def add_channel():
    new_channel.set(False)
    logger.error("Adding a new channel")


def add_video_to_db():
    logger.error("Adding video to db")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(
        router=router,
    )

    with solara.Column(classes=["main-container"]):
        solara.Markdown("## Add A New Video")
        with solara.Card():
            solara.InputText(
                "Enter a URL or YouTube Video ID",
                value=video_url,
                continuous_update=False,
            )
            solara.Button("Add Video", on_click=add_video, classes=["button"])

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
            solara.Button(
                "Add Channel",
                classes=["button"],
                disabled=not new_channel,
                on_click=add_channel,
            )

        with solara.Card():
            # thumbnail image here
            solara.Markdown("## Video Info")
            solara.InputText("Title", value=video_title)
            solara.InputText("Description", value=video_description)
            solara.InputText("Duration", value=video_duration)
            solara.InputText("Upload Date", value=video_upload_date)
            solara.Button(
                "Add Video",
                classes=["button"],
                disabled=not new_channel,
                on_click=add_video_to_db,
            )
