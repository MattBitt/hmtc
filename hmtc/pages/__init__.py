import solara
from loguru import logger
from hmtc.main import setup
from pathlib import Path
import shutil


db, config = setup()

if config.get("GENERAL", "CLEAN_DOWNLOADS") == True:
    download_folder = Path(config.get("GENERAL", "DOWNLOAD_PATH"))
    for f in download_folder.glob("*"):
        logger.warning(f"Removing existing file in downloads: {f}")
        f.unlink()

app_state = solara.reactive(0)


solara.Style(Path("hmtc/assets/style.css"))
