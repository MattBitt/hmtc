import solara
from loguru import logger
from pathlib import Path
import shutil
from hmtc.config import init_config
from hmtc.utils.my_logging import setup_logging
from hmtc.db import init_db
from hmtc.models import db_null


def setup():
    config = init_config()
    setup_logging(config)
    db_instance = init_db(db_null, config)
    return db_instance, config


logger.debug("very beginning")
db, config = setup()
logger.debug(f"Current Running Mode = {config.get('GENERAL', 'RUNNING_MODE')}")
logger.debug("after setup")

if config.get("GENERAL", "CLEAN_DOWNLOADS") == True:
    download_folder = Path(config.get("GENERAL", "DOWNLOAD_PATH"))
    for f in download_folder.glob("*"):
        logger.warning(f"Removing existing file in downloads: {f}")
        f.unlink()

# this was in the default scheme
# not quite sure how to use it yet though
app_state = solara.reactive(0)


solara.Style(Path("hmtc/assets/style.css"))

logger.debug("end of pages/__init__")
