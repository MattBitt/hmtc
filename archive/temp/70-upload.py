from pathlib import Path
from typing import List, TypedDict

import solara
from loguru import logger

from hmtc.components.shared.progress_slider import SimpleProgressBar

clicks = solara.reactive(0)


class FileInfo(TypedDict):
    name: str  # file name
    size: int  # file size in bytes
    # file_obj: BinaryIO
    data: bytes  # only present if lazy=False


@solara.component
def FileDropCard():
    filename, set_filename = solara.use_state("")
    size, set_size = solara.use_state(0)
    progress_complete = solara.use_reactive(0)

    def on_file(files: List[FileInfo]):
        logger.debug(f"Files: {[f["name"] for f in files]}")
        for f in files:
            set_filename(f["name"])
            set_size(f["size"])
            # set_content(f["file_obj"].read(100))
            path = Path(config.get("PATHS", "UPLOAD")) / f["name"]
            if f["data"] is not None:
                with open(path, "wb") as out_file:
                    out_file.write(f["data"])

    def update_progress(progress: float):
        progress_complete.set(progress)

    with solara.Card():

        SimpleProgressBar("Progress", progress_complete.value, 100)
        solara.FileDropMultiple(
            label="Drag and drop a file here to read the first 100 bytes.",
            on_file=on_file,
            on_total_progress=update_progress,
            lazy=False,
        )

        file = Path(filename)

        solara.Info(
            f"File uploaded: name:{file.name} suffix: {file.suffix} size: {size} bytes"
        )
        solara.Info(f"File {filename} has total length: {size}\n, first 100 bytes:")


@solara.component
def Page():
    with solara.Card():

        solara.Markdown("## Upload File")
        FileDropCard()
