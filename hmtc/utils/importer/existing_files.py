from pathlib import Path
from typing import List

from loguru import logger

from hmtc.models import Video
from hmtc.utils.youtube_functions import get_youtube_id


def import_existing_video_files_to_db(path):
    # havent tested in a million years, but might be a good starting point
    # for the file import
    found = 0
    unfound = 0
    f = Path(path)
    for file in f.glob("**/*.*"):
        if file.is_file():
            youtube_id = get_youtube_id(file.stem)
            if youtube_id:
                vid = Video.get_or_none(Video.youtube_id == youtube_id)
                if not vid:
                    unfound = unfound + 1
                    continue
                else:
                    logger.debug(
                        f"Successfully found video{vid.youtube_id}. Adding file"
                    )
            else:
                logger.debug(f"Could not find youtube_id in {file}")

    logger.success("Finished importing files to the database.")
    logger.debug(f"Found {found} new files.")
    logger.debug(f"There were {unfound} files found with no associated video")

    if not f.exists():
        logger.error("Path not found")
        return None
    return f.glob("**/*")
