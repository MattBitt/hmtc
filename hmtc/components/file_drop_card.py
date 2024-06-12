from typing import BinaryIO, TypedDict

import solara

from hmtc.components.progress_slider import SimpleProgressBar


class FileInfo(TypedDict):
    name: str  # file name
    size: int  # file size in bytes
    file_obj: BinaryIO
    data: bytes  # only present if lazy=False


@solara.component
def FileDropCard(on_file, lazy=False):

    progress_complete = solara.use_reactive(0)

    def update_progress(progress: float):
        progress_complete.set(progress)

    with solara.Card():

        SimpleProgressBar("Progress", progress_complete.value, 100)
        solara.FileDrop(
            label="Drag and drop a file here.",
            on_file=on_file,
            on_total_progress=update_progress,
            lazy=lazy,
        )
