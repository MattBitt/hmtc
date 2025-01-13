from pathlib import Path
from typing import List

from loguru import logger

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.base_domain import BaseDomain
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import Video as VideoModel
from hmtc.models import db_null
from hmtc.utils.youtube_functions import parse_youtube_info_file

config = init_config()
db_instance = init_db(db_null, config)
STORAGE = config["STORAGE"]


def get_files_in_folder(folder: Path) -> List[Path]:
    return list(folder.glob("*"))


def youtube_id_in_db(youtube_id: str) -> bool:
    return (
        Video.repo.model.select()
        .where(Video.repo.model.youtube_id == youtube_id)
        .exists()
    )


def is_valid_youtube_id(youtube_id: str) -> bool:
    if len(youtube_id) != 11 or " " in youtube_id:
        # not sure what other checks i should do here
        return False
    return True


def check_for_sections(description: str) -> None:

    logger.debug("Checking for sections")
    lines = description.split("\n")
    section_line = 0
    for index, line in enumerate(lines):
        if line.lower().startswith("instrumentals"):
            logger.debug(f"Found Instrumental at {index}")
            section_line = index + 1
            break
    if section_line > 0:
        for line in lines[section_line:]:
            if line == "":
                break
            logger.warning(f"Found a new section {line}")
            # add the line to the instrumental section


def create_video_from_folder(path: Path) -> None:
    # check for an info file. if there is one, use it to create the video
    # if there isn't one, skip it
    files = list(path.glob("*"))
    info_file = [x for x in files if x.name.endswith(".info.json")]
    if info_file:
        logger.debug(f"Creating video {path.stem}")

        # read the data
        data = parse_youtube_info_file(info_file[0])
        _channel = data.pop("channel")
        channel = Channel.get_by(youtube_id=_channel["youtube_id"])
        if channel is None:
            channel = Channel.create(_channel)
        data["channel_id"] = channel.instance.id
        vid = Video.create(data)

        # add the files to the db
        for file in files:
            if file.name == "album.nfo":
                file.unlink()  # cleaning up old stuff 1-12-25
                continue
            if "Zone.Identifier" in file.name:
                logger.debug(f"Deleting {file.name}")
                file.unlink()
                continue
            Video.add_file(vid, file)

        logger.success(f"Created video {vid.instance.title}")
        # if "omegle" in vid.title.lower():
        #     # FUTURE ...
        #     sections = check_for_sections(vid.description) or []
        #     for section in sections:
        #         # Section.create(vid, section)
        #         pass
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


def verify_files(item: BaseDomain, path: Path):
    logger.debug(f"Verifying Files for {item} and path {path}")
    # for file in item.files()
    #   is file in the folder?
    #   files_not_in_folder.append()

    # for file in path.files()
    #   is file in the db?
    #   files_not_in_db.append()
    num_files_in_db = item.file_repo.num_files(item.instance.id)

    files_in_folder = [f for f in path.iterdir() if f.is_file()]
    num_files_in_folder = len(files_in_folder)
    if num_files_in_db == num_files_in_folder:
        logger.debug(
            f"Number of Files equal {num_files_in_db}. Not checking more in depth"
        )
    else:
        logger.warning(f"File mismatch for {item}")
        logger.warning(f"DB: {num_files_in_db}\tFolder: {num_files_in_folder}")


def import_existing_video_files_to_db(path):
    # set to_process as the iterations desired
    to_process = 10
    circuit_breaker = 0

    for item in path.glob("*"):

        if circuit_breaker > to_process:
            break

        if item.is_dir():
            if len(str(item.stem)) == 4 and str(item.stem).isnumeric():
                # files are likely their final resting place already
                # need to check each subfolder to for files in the database
                logger.debug(
                    f"Found folder {item} on the disk. Need to loop through to check files"
                )
                for subfolder in item.glob("*"):
                    if is_valid_youtube_id(subfolder.stem):
                        # found a folder for an existing video
                        # probably nothing to do here, but
                        # should check the files in the folder
                        # match whats in the database
                        vid = (
                            VideoModel.select()
                            .where(VideoModel.youtube_id == subfolder.stem)
                            .get_or_none()
                        )
                        if vid is None:
                            create_video_from_folder(subfolder)
                        else:
                            verify_files(Video(vid), subfolder)

            elif is_valid_youtube_id(item.stem):
                # this will search the 'root' videos path for
                # existing files and then move them to the
                # /yyyy/youtube_id folder as needed
                # it should then remove the folder if its empty

                if not any(item.iterdir()):
                    item.rmdir()  # remove empty folders
                elif youtube_id_in_db(item.stem):
                    # this doesn't work since vid isn't defined
                    # need to rework the functions above for their
                    # ergonomics.
                    verify_files(Video(vid), item)
                    

                else:
                    create_video_from_folder(item)
                    for bad_file in item.glob("*Zone.Indentifier*"):
                        bad_file.unlink()
                    if not any(item.iterdir()):
                        item.rmdir()  # remove empty folders
                    circuit_breaker += 1

            else:
                logger.debug(f"Skipping invalid youtube id {item.stem}")
        elif item.is_file():
            logger.error(
                f"Shouldn't be any files in the 'root' folder. Skipping {item}"
            )
    logger.success("Finished importing files to the database.")


if __name__ == "__main__":
    from hmtc.utils.importer.seed_database import recreate_database

    recreate_database()
    import_existing_video_files_to_db(STORAGE / "videos")
