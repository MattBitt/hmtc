from pathlib import Path

import solara
from loguru import logger

from hmtc.components.video.files_panel import FilesPanel
from hmtc.components.video.info_dialog_buttons import InfoDialogButtons
from hmtc.components.video.jf_panel import JFPanel
from hmtc.components.video.section_dialog_button import SectionDialogButton
from hmtc.config import init_config

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"
MIN_SECTION_LENGTH = 60
MAX_SECTION_LENGTH = 1200
AVERAGE_SECTION_LENGTH = 180
IMG_WIDTH = "300px"
loading = solara.reactive(False)


@solara.component
def TopRow(video, reactive_sections):
    # VideoInfoInputCard.vue
    # Buttons 1, 2, 3
    with solara.Row(justify="center"):
        InfoDialogButtons(
            video=video,
        )
        # Button 4
        FilesPanel(
            video=video,
        )
        # Button 5
        SectionDialogButton(
            video=video,
            reactive_sections=reactive_sections,
        )
        # Button 6 (jellyfin icon)
        JFPanel(
            video=video,
        )
