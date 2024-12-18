from pathlib import Path
from typing import List

from loguru import logger

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains import Video
from hmtc.domains.channel import Channel
from hmtc.models import db_null
from hmtc.utils.youtube_functions import parse_youtube_info_file

config = init_config()
db_instance = init_db(db_null, config)
STORAGE = config["STORAGE"]


def get_files_in_folder(folder: Path) -> List[Path]:
    return list(folder.glob("*"))


def youtube_id_in_db(youtube_id: str) -> bool:
    return Video.youtube_id_exists(youtube_id)


def is_valid_youtube_id(youtube_id: str) -> bool:
    if len(youtube_id) != 11 or " " in youtube_id:
        # not sure what other checks i should do here
        return False
    return True


def create_video_from_folder(path: Path) -> None:
    # check for an info file. if there is one, use it to create the video
    # if there isn't one, skip it
    files = path.glob("*")
    info_file = [x for x in files if x.name.endswith(".info.json")]
    if info_file:
        logger.debug(f"Creating video {path.stem}")

        # read the data
        data = parse_youtube_info_file(info_file[0])

        # create the video and channel (if it doesn't exist)
        vid = Video.create(data)

        # add the rest of the files to the video
        for file in files:
            if file != info_file[0]:
                Video.add_file_to_video(vid, file)

        logger.success(f"Created video {vid.title}")
    else:
        logger.debug(f"Skipping video {path.stem}")


def update_existing_video_from_existing_files(path: Path) -> None:
    # FUTURE ...
    logger.debug(f"Updating video {path.stem}")


def delete_superchats_if_exist(path: Path) -> None:
    superchat_folder = path / "superchats"
    if superchat_folder.exists():
        logger.debug(f"Deleting superchats for {path.stem}")
        for file in superchat_folder.glob("*"):
            file.unlink()
        superchat_folder.rmdir()


def replace_files_for_existing_video(path: Path) -> None:
    # FUTURE ...
    # delete all files for the video
    # download new files for the video
    logger.debug(f"Replacing files for {path.stem}")


def import_existing_video_files_to_db(
    path,
    update_existing_records=False,
    replace_files=False,
    delete_premigration_superchats=False,
):

    for item in path.glob("*"):
        if item.is_dir():
            if is_valid_youtube_id(item.stem):
                if youtube_id_in_db(item.stem):
                    # this is what will be used once the database is stood up
                    if update_existing_records:
                        logger.debug(f"Updating existing youtube id {item.stem}")
                        update_existing_video_from_existing_files(item)
                    if replace_files:
                        logger.debug(f"Replacing existing youtube id {item.stem}")
                        replace_files_for_existing_video(item)
                    else:
                        logger.debug(f"Skipping existing youtube id {item.stem}")
                else:
                    # this is what will be used to get the database up and running
                    if delete_premigration_superchats:
                        delete_superchats_if_exist(item)

                    files = get_files_in_folder(item)
                    logger.debug(f"Found {len(files)} files for {item.stem}")
                    create_video_from_folder(item)

                    logger.debug(f"Skipping existing youtube id {item.stem}")
            else:
                logger.debug(f"Skipping invalid youtube id {item.stem}")
        elif item.is_file():
            logger.error(
                f"Shouldn't be any files in the 'root' folder. Skipping {item}"
            )
    logger.success("Finished importing files to the database.")
    # logger.debug(f"Found {found} new files.")
    # logger.debug(f"There were {unfound} files found with no associated video")


if __name__ == "__main__":
    import_existing_video_files_to_db(
        STORAGE / "videos", delete_premigration_superchats=True
    )
