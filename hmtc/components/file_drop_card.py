import solara
from hmtc.config import init_config
from hmtc.components.progress_slider import SimpleProgressBar

from typing import List, Optional, Callable, BinaryIO, TypedDict
import textwrap
from pathlib import Path
from loguru import logger

clicks = solara.reactive(0)
config = init_config()


class FileInfo(TypedDict):
    name: str  # file name
    size: int  # file size in bytes
    # file_obj: BinaryIO
    data: bytes  # only present if lazy=False


@solara.component
def FileDropCard(on_file):

    progress_complete = solara.use_reactive(0)

    def update_progress(progress: float):
        progress_complete.set(progress)

    with solara.Card():

        SimpleProgressBar("Progress", progress_complete.value, 100)
        solara.FileDrop(
            label="Drag and drop a file here.",
            on_file=on_file,
            on_total_progress=update_progress,
            lazy=False,
        )
