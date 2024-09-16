import solara
from loguru import logger
from pathlib import Path
from hmtc.schemas.video import VideoItem
from hmtc.utils.jf import (
    grab_now_playing,
    jellyfin_sessions,
    jellyfin_playpause,
    jellyfin_connection_test,
    jellyfin_seekto,
    jellyfin_loop_2sec,
)


def get_youtube_id(filename):
    fn = Path(filename).stem
    if "___" not in fn:
        return None
    return fn.split("___")[1]


def seek_forward(ms, *ignore_args):
    pass


@solara.component
def JellyfinSessionInfo(session):
    with solara.Card():
        with solara.Row(justify="space-between"):
            solara.Markdown(f"#### User: {session['UserName']}")
            solara.Markdown(f"#### Client: {session['Client']}")
            solara.Markdown(f"#### Device: {session['DeviceName']}")
        # solara.Markdown(f"#### Device ID: {session['DeviceId']}")


@solara.component
def JellyfinPanel(current_video_youtube_id: str, current_section, status, jf_session):
    status = "status-red"  # or 'status-green'

    def refresh_jellyfin():
        # need to move this to the parent component so i can use it in the modal
        logger.debug("Refreshing Jellyfin Sessions")
        jf_session.set(jellyfin_sessions())

    def move_to_section_start(section):
        logger.debug(f"Moving to start of section: {section.start} seconds")
        jellyfin_seekto(section.start)

    this_session = jf_session.value
    JellyfinSessionInfo(jf_session.value)
    now_playing = grab_now_playing(session=this_session)

    if now_playing:
        if now_playing["type"] == "track":
            solara.Markdown("### This is a track playing, somehow....")
        else:
            # this only works since i control the video naming
            # need a better solution
            # 8-30-24
            youtube_id = get_youtube_id(now_playing["path"])

            vid = VideoItem.get_by_youtube_id(youtube_id)
            if vid is None:
                solara.Text(f"● Jellyfin", classes=[status])
                logger.debug(
                    f"Video with youtube_id {youtube_id} not found in database"
                )
                return
            if current_video_youtube_id != vid.youtube_id:
                with solara.Row():
                    solara.Text(f"● Jellyfin", classes=[status])

                logger.debug(
                    "This video that is playing is not the video shown on the page. Disabling controls"
                )
            else:
                status = "status-green"
                solara.Text(f"● Jellyfin", classes=[status])
                logger.debug(f"#### Video Title: {vid.title}")
                with solara.ColumnsResponsive():
                    with solara.Column():
                        solara.Markdown(f"- Video ID: {youtube_id}")
                        # solara.Markdown(f"- Jellyfin ID: {now_playing['jf_id']}")

                        solara.Markdown(
                            f"- Current Position: {now_playing['position']} ({now_playing['status']})"
                        )
                        # solara.Markdown(
                        #     f"- Currently Playing Type: {now_playing['type']}"
                        # )
                        with solara.Row():
                            solara.Button(
                                "Play/Pause",
                                classes=["button"],
                                on_click=jellyfin_playpause,
                            )
                            solara.Button(
                                "Connection Test",
                                classes=["button"],
                                on_click=jellyfin_connection_test,
                            )
                            solara.Button(
                                "Refresh",
                                classes=["button"],
                                on_click=refresh_jellyfin,
                            )
                        if current_section is not None:
                            with solara.Row():
                                solara.Button(
                                    "Jump to Section Start",
                                    classes=["button"],
                                    on_click=lambda: move_to_section_start(
                                        current_section
                                    ),
                                )
                                solara.Button(
                                    "Loop Section Start",
                                    classes=["button"],
                                    on_click=lambda: jellyfin_loop_2sec(
                                        session_id=this_session.id,
                                        position=current_section.start,
                                    ),
                                )
                                solara.Button(
                                    "Loop Section End",
                                    classes=["button"],
                                    on_click=lambda: jellyfin_loop_2sec(
                                        session_id=this_session.id,
                                        position=current_section.end - 2,
                                    ),
                                )
