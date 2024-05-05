from typing import Callable, List, TypedDict

import solara

from hmtc.components.progress_slider import SimpleProgressBar

clicks = solara.reactive(0)


class FileInfo(TypedDict):
    name: str  # file name
    size: int  # file size in bytes
    # file_obj: BinaryIO
    data: bytes  # only present if lazy=False


@solara.component
def FileDropMultiCard(on_file: Callable[[List[FileInfo]], None] = None):

    progress_complete = solara.use_reactive(0)

    def update_progress(progress: float):
        progress_complete.set(progress)

    with solara.Card():

        SimpleProgressBar("Progress", progress_complete.value, 100)
        solara.FileDropMultiple(
            label="Drag and drop a file here.",
            on_file=on_file,
            on_total_progress=update_progress,
            lazy=False,
        )
