import solara
from loguru import logger

from hmtc.components.file_drop_card import FileDropCard, FileInfo
from hmtc.components.searchable_textbox import SearchableTextbox
from hmtc.models import Playlist


def write_to_disk(file: FileInfo):
    logger.debug(f"Writing file to disk: {file['name']}")

    with open(file["file_obj"], "wb") as src_file:
        src_file.write(file["data"])

    return file["name"]


@solara.component
def SourceSearchCard(query, choice, process_file):
    def clear():
        query.value = ""
        choice.value = "Detect"

    def search():
        logger.debug(f"Searching for {query.value} of type {choice.value}")
        match choice.value:
            case "Auto":
                logger.debug("Auto detected")
            case "Detect":
                logger.debug("Detecting source type")
            case "Channel":
                logger.debug("Channel selected")
            case "Playlist":
                logger.debug("Playlist selected")
                if not query.value:
                    logger.error("No query value")
                else:
                    Playlist.create_from_yt_id(query.value)

            case "Video":
                logger.debug("Video selected")

    with solara.ColumnsResponsive(12, large=6):
        with solara.Card():
            solara.Markdown("## Add a source by entering a youtube id below.")

            solara.Select(
                label="Select a source type",
                values=["Detect", "Channel", "Playlist", "Video"],
                value=choice,
            )
            with solara.Row():
                SearchableTextbox(
                    label="Enter a youtube id",
                    input_text=query,
                    continuous_update=False,
                )
                solara.Button("Search", on_click=search)
                solara.Button("Clear", on_click=clear)

                solara.Markdown(f"searching for {query.value}")
                solara.Markdown(f"source type: {choice.value}")
        with solara.Card():
            solara.Markdown("## Add a source by dragging an info file below")
            FileDropCard(on_file=process_file, lazy=False)


@solara.component
def Page():
    file_dropped = solara.use_reactive(False)

    def process_file(file: FileInfo):
        filename = write_to_disk(file)
        logger.debug(f"Processing file {filename}")
        file_dropped.set(True)
        return filename

    query = solara.use_reactive("")
    source_type = solara.use_reactive("Auto")
    SourceSearchCard(query=query, choice=source_type, process_file=process_file)
