from pathlib import Path

import PIL
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.assets.icons.icon_repo import Icons
from hmtc.models import Section as SectionModel
from hmtc.utils.time_functions import seconds_to_hms, time_ago_string

IMG_WIDTH = "300px"


@solara.component
def ProcessingCard():
    with solara.Card(
        classes=["processing-card"],
        style={"background-color": Colors.dark_gray},
    ):
        with solara.Row(justify="center"):
            solara.Text("Processing...", classes=["processing-text"])


@solara.component
def VideoInfoPanel(video_domain):
    video = video_domain.instance
    is_unique = solara.use_reactive(video.unique_content)
    sections = SectionModel.select(
        SectionModel.id, SectionModel.start, SectionModel.end
    ).where(SectionModel.video_id == video.id)

    def mark_unique():
        video.unique_content = True
        video.save()
        is_unique.set(True)
        logger.info(f"Marked {video.title} 'UNIQUE'")

    def mark_nonunique():
        video.unique_content = False
        video.save()
        is_unique.set(False)
        logger.info(f"Marked {video.title} 'UNIQUE'")

    section_durations = [
        (x.end - x.start) / 1000 for x in sections
    ]  # list of sections in seconds

    section_percentage = sum(section_durations) / video.duration * 100
    num_sections = len(sections)
    num_segments = 0

    with solara.Row(justify="center"):
        solara.Text(
            f"{video.title[:80]}",
            classes=["video-info-text"],
        )
    with solara.Columns([6, 6]):
        with solara.Column():
            with solara.Row(justify="center"):
                solara.Image(video_domain.poster(), width=IMG_WIDTH)
            with solara.Columns([6, 6]):
                with solara.Column():
                    with solara.Row(justify="center"):
                        solara.Text(
                            f"Uploaded: {time_ago_string(video.upload_date)}",
                            classes=["medium-timer"],
                        )
                    with solara.Row(justify="center"):
                        solara.Text(
                            f"Length: {seconds_to_hms(video.duration)}",
                            classes=["medium-timer"],
                        )
                with solara.Column():
                    if is_unique.value:
                        solara.Button(
                            f"NOT unique",
                            on_click=mark_nonunique,
                            classes=["button"],
                        )
                    else:
                        solara.Button(
                            f"UNIQUE", on_click=mark_unique, classes=["button"]
                        )
        with solara.Column():
            # if len(section_durations) > 0:
            #     solara.Markdown(
            #         f"Sections: {len(section_durations)} ({section_percentage:.2f}%)"
            #     )

            # with solara.Link(f"utils/frame-analyzer/{video.id}"):
            #     solara.Button(
            #         label="Frame Analyzer",
            #         classes=["button"],
            #     )
            # with solara.Link(f"/superchat-fine-tuner/{video.id}"):
            #     solara.Button(
            #         label="Superchat Fine Tuner",
            #         icon_name=Icons.SUPERCHAT.value,
            #         classes=["button"],
            #     )

            # with solara.Link(f"/domains/superchat-control-panel/{video.id}"):
            #     solara.Button(
            #         label="Search for Superchats",
            #         icon_name=Icons.SEARCH.value,
            #         classes=["button"],
            #     )

            # if len(video.superchats) > 0:
            #     with solara.Link(f"/superchat-segments/{video.id}"):
            #         solara.Button(
            #             label=f"Segments ({num_segments})",
            #             icon_name=Icons.SUPERCHAT_SEGMENT.value,
            #             classes=["button"],
            #         )

            # if len(video.superchats) > 0:
            #     with solara.Link(f"/superchat-segments/long-enough/{video.id}"):
            #         solara.Button(
            #             label=f"Segments (Long Enough)",
            #             icon_name=Icons.SUPERCHAT_SEGMENT.value,
            #             classes=["button"],
            #         )
            with solara.Link(f"/api/videos/sectionalizer/{video.id}"):
                solara.Button(
                    label=f"Sectionalizer",
                    icon_name=Icons.SECTION.value,
                    classes=["button"],
                )

            with solara.Link(f"/api/videos/finetuner/{video.id}"):
                solara.Button(
                    label=f"Fine Tuner",
                    icon_name=Icons.FINETUNER.value,
                    classes=["button"],
                    disabled=(num_sections == 0),
                )
            with solara.Link(f"/api/videos/superchatextractor/{video.id}"):
                solara.Button(
                    label=f"Superchat Extractor",
                    icon_name=Icons.SUPERCHAT.value,
                    classes=["button"],
                    disabled=False,
                )
