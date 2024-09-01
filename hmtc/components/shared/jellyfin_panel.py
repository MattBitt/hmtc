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
def JellyfinPanel(current_video_youtube_id: str, current_section):

    user_sessions = solara.use_reactive(jellyfin_sessions())

    def refresh_jellyfin():
        logger.debug("Refreshing Jellyfin Sessions")
        user_sessions.set(jellyfin_sessions())

    def move_to_section_start(section):
        logger.debug(f"Moving to start of section: {section.start} seconds")
        jellyfin_seekto(section.start)

    with solara.Column():
        solara.Button("Refresh", classes=["button"], on_click=refresh_jellyfin)
    if user_sessions.value is None:
        logger.error("Unable to login to jellyfin")
        return

    if len(user_sessions.value) == 0:
        solara.Markdown("### No sessions found")
        return

    if len(user_sessions.value) > 1:
        solara.Markdown("### Multiple sessions found")
        solara.Markdown("### Choose a Device")
        for sess in user_sessions.value:
            JellyfinSessionInfo(sess)

    else:

        JellyfinSessionInfo(user_sessions.value[0])
        now_playing = grab_now_playing(session=user_sessions.value[0])

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
                    solara.Warning(
                        f"Video with youtube_id {youtube_id} not found in database"
                    )
                    return
                if current_video_youtube_id != vid.youtube_id:
                    with solara.Warning():
                        solara.Markdown(
                            f"This video that is playing is not the video shown on the page. Disabling controls"
                        )
                else:
                    with solara.Success():
                        solara.Markdown(f"#### Video Title: {vid.title}")
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
                                            current_section.start
                                        ),
                                    )
                                    solara.Button(
                                        "Loop Section End",
                                        classes=["button"],
                                        on_click=lambda: jellyfin_loop_2sec(
                                            current_section.end - 2
                                        ),
                                    )

        else:

            solara.Markdown("### Found a session, No video currently playing")
