import re
import subprocess
from datetime import date, datetime
from glob import glob
from pathlib import Path

import crud
import models
import schemas
import yaml
from configs import cnf
from db import Base, db_session, engine
from my_logging import logger
from utils import move_file, write_dict_to_yaml
from yt_dlp_functions import (download_files, get_collection_url_list,
                              get_json_info)


def parse_yaml(yaml_file):
    with open(yaml_file, "r") as file:
        yaml_dict = yaml.safe_load(file)
    return yaml_dict


def move_to_already_imported(already_imported):
    input_file = cnf.APP_CONFIG.individual_videos_input_file
    output_file = cnf.APP_CONFIG.individual_videos_output_file


def read_urls_from_db():
    # needs to check the db for all urls
    # for now, assume that nothing is in the db by returning []
    session = db_session()
    urls = crud.SourceRepo.fetchURLs(session)
    session.close()
    return urls


def find_episode_number(text: str, patterns: list) -> str:
    if text == "" or patterns == []:
        logger.error("No text or pattern found {} {}", text, patterns)
        raise KeyError
    for pattern in patterns:
        # logger.debug("Pattern = {}", pattern)
        pattern = re.compile(pattern)
        result = pattern.search(text)
        if result is not None:
            return str(result.groups(1)[0]).zfill(3)

    logger.warning("No Match found for {}", text)
    return ""


def convert_upload_date(upload_date):
    # example date format from youtube: '20190724'
    format = "%Y%m%d"
    upload_date_formatted = datetime.strptime(upload_date, format)
    return upload_date_formatted


def count_album_name_in_db(album_name):
    session = db_session()
    album = crud.AlbumRepo.fetchByAlbumName(album_name=album_name, session=session)
    if not album:
        return 0  # meaning this album doesn't exist yet
    album_id = album.id
    num_on_album = crud.SourceRepo.fetchCountByAlbum(album_id=album_id, session=session)
    session.close()
    return num_on_album


def get_or_create_album(album_name, track_prefix):
    # need to check if album exists
    album_data = {}
    # check if album already exists
    session = db_session()
    album = crud.AlbumRepo.fetchByAlbumName(album_name=album_name, session=session)
    session.close()
    if not album:
        album_data = {
            "album_name": album_name,
            "track_prefix": track_prefix,
            "path": "/tracks/",
        }
        album_schema = schemas.AlbumBaseSchema(**album_data)
        album_model = models.Album(**album_schema.dict())
        album = crud.AlbumRepo.create(db_object=album_model, session=session)
    return album.id


def create_source_dict(collection, url, metadata):
    if "ignore" in collection.keys():
        ignore = True
        album_name = "Ignored"
        file_base = "Ignored"
        track_prefix = "Ignored"
        upload_date = datetime.today()
        metadata["collection_name"] = ""
    else:
        ignore = False
        upload_date = convert_upload_date(metadata["upload_date"])
        if "track_prefix" in collection:
            track_prefix = collection["track_prefix"]
        else:
            track_prefix = ""
        if "album_prefix" in collection.keys():
            # this means that i want a separate album for each episode
            episode_number = find_episode_number(
                metadata["fulltitle"], collection["episode_number_patterns"]
            )
            album_name = collection["album_prefix"] + " " + episode_number
            file_base = album_name
            if "collection_name" in collection.keys():
                metadata["collection_name"] = collection["collection_name"]
            else:
                metadata["collection_name"] = album_name

        elif "album_name" in collection.keys():
            # this means that i want a single album to contain all of these videos
            # need to compute episode_number
            album_name = collection["album_name"]
            num_in_db = count_album_name_in_db(album_name)
            file_base = album_name + " " + str(num_in_db + 1).zfill(3)
            if "collection_name" in collection.keys():
                metadata["collection_name"] = collection["collection_name"]
            else:
                metadata["collection_name"] = album_name
        else:
            album_name = collection["collection_name"]
            metadata["collection_name"] = album_name
            num_in_db = count_album_name_in_db(album_name)
            file_base = album_name + " " + str(num_in_db + 1).zfill(3)

    album_id = get_or_create_album(album_name, track_prefix)
    source = {
        "url": url,
        "video_title": metadata["fulltitle"],
        "ignore": ignore,
        "upload_date": upload_date,
        "album_id": album_id,
        "duration": metadata["duration"] * 1000,
        "filename_base": file_base,
        "collection_name": metadata["collection_name"],
    }

    return source


def add_source_to_db(source_dict):
    model = models.Source
    repo = crud.SourceRepo
    schema = schemas.SourceBaseSchema
    logger.debug("Adding new video to Database {}".format(source_dict["video_title"]))
    add_to_db(source_dict, model, repo, schema)


def add_album_to_db(album_dict):
    model = models.Album
    repo = crud.AlbumRepo
    schema = schemas.AlbumBaseSchema
    add_to_db(album_dict, model, repo, schema)


def add_to_db(data_to_add, model, repo, schema):
    data = schema(**data_to_add)
    data_model = model(**data.dict())
    session = db_session()
    repo.create(data_model, session)
    session.close()
    return 201


def is_url_in_db(url):
    session = db_session()
    result = crud.SourceRepo.fetchByURL(url=url, session=session)
    session.close()
    return result is not None

    # urls_in_db = read_urls_from_db()
    # for src in urls_in_db:
    #     if url == src:
    # before checking anything else, see if its already in the db
    # if it is, no work to do
    # return True


def is_url_in_individual_video(url, individual_videos):
    for vid in individual_videos["videos"]:
        if url == vid["url"]:
            # for each url, check the individual video list to see if its already there
            # if it is, process it with the later videos
            # logger.debug("{} already in ind_videos".format(url))
            return True
    return False


def check_for_existing_url(url: str, individual_videos):
    return is_url_in_db(url) or is_url_in_individual_video(url, individual_videos)


def individual_video_entry_data(url, metadata):
    return {
        "url": url,
        "album_name": "NEED ALBUM NAME",
        "collection_name": "NEED COLLECTION NAME OR USE ALBUM NAME BY DELETING",
        "video_title": metadata["fulltitle"],
        "ignore": False,
    }


def default_indvidual_video_entry_data(url):
    return {
        "url": url,
        "album_name": "",
        "collection_name": "",
        "video_title": "",
        "ignore": False,
    }


def get_source_metadata(url):
    try:
        metadata = get_json_info(url)
    except Exception:  # this is a bare except because the yt-dlp error is crazy...
        # logger.error("Unable to download source: {}".format(url))
        return None
    logger.debug("Successfully downloaded metadata for {}".format(url))
    return metadata


def add_individual_video_to_db(vid):
    ind_vids = vid["videos"]
    for vids in ind_vids:
        url = vids["url"]
        if not is_url_in_db(url):
            metadata = get_source_metadata(url)
            if metadata:
                source = create_source_dict(vids, url, metadata)
                add_source_to_db(source)
            else:
                logger.error("Unable add {} to db".format(url))
                logger.error(
                    "Why is this added to individual if I can't download it? {}".format(
                        url
                    )
                )


def get_error_videos():
    error_file = cnf.APP_CONFIG.video_collection_error_videos
    if not Path(error_file).exists():
        # there is no error file, so nothing to check
        return []
    error_videos = parse_yaml(error_file)

    return error_videos


def is_in_error_videos(url, error_videos):
    for ev in error_videos:
        if url == ev["url"]:
            return True

    return False


def is_time_to_retry(url, error_videos):
    # need to find url in error videos
    # check the date it was added
    todays_date = date.today()
    for ev in error_videos:
        if url == ev["url"]:
            if (todays_date - ev["date_added"]).days < 7:  # within a week
                return True
            if todays_date.day == 1:  # retry old videos on the first of each month
                return True
            else:
                return False
    return False


def add_collections_to_db(individual_videos):
    input_file = cnf.APP_CONFIG.video_collections_input_file
    # should probably create a 'get_video_collections' function to check if the input file exists
    video_collections = parse_yaml(input_file)
    error_videos = get_error_videos()
    error_video_entries = []
    for channel in video_collections["channels"]:
        for collection in channel["collections"]:
            urls = get_collection_url_list(collection)
            for url in urls:
                is_old_error_video = is_in_error_videos(url, error_videos)
                should_retry_error_videos = not is_old_error_video or is_time_to_retry(
                    url, error_videos
                )

                if (
                    not is_url_in_db(url)
                    and not is_url_in_individual_video(url, individual_videos)
                    and should_retry_error_videos
                ):
                    metadata = get_source_metadata(url)
                    if metadata:
                        # need to delete the error video from the yaml
                        # i think this is where that should be.
                        source = create_source_dict(collection, url, metadata)
                        add_source_to_db(source)
                    else:
                        logger.error("Unable to download metadata for {}".format(url))
                        # only add it to the list if not already there
                        # dont want to reset the date each time
                        if not is_old_error_video:
                            entry_data = default_indvidual_video_entry_data(url)
                            # use this to determine how often to check again
                            # may be helpful if new videos are posted as private and then
                            # turned to public when they are released
                            entry_data["date_added"] = date.today()

                            entry_data["collection_name"] = collection[
                                "collection_name"
                            ]
                            error_video_entries.append(entry_data)
                    logger.debug("Downloaded metadata for {}".format(url))
                else:
                    pass
                    # logger.debug("{} already exists".format(url))
    if len(error_video_entries) > 0:
        # make sure to append to the error file
        # need to check and see if it was already in the error file
        write_dict_to_yaml(
            error_video_entries, "a", cnf.APP_CONFIG.video_collection_error_videos
        )


def add_rest_of_videos_to_db():
    # after adding everything from the collections and individual videos yaml files
    # download all of the videos from any channels and write the
    # urls not included to a yaml file
    input_file = cnf.APP_CONFIG.video_collections_input_file
    video_collections = parse_yaml(input_file)
    new_video_entries = []
    for channel in video_collections["channels"]:
        collection = {
            "collection_name": channel["channel_name"],
            "url": channel["url"],
        }
        urls = get_collection_url_list(collection)
        urls_in_db = read_urls_from_db()

        for url in urls:

            if url not in urls_in_db:
                if "shorts" not in url:  # ignore shorts on the channel
                    metadata = get_source_metadata(url)
                    if metadata:
                        entry_data = individual_video_entry_data(url, metadata)
                    else:
                        entry_data = default_indvidual_video_entry_data(url)
                    new_video_entries.append(entry_data)
    if len(new_video_entries) > 0:
        write_dict_to_yaml(new_video_entries, "w", "config/new_video_entries.yaml")


def parse_individual_videos():
    input_file = cnf.APP_CONFIG.individual_videos_input_file
    yaml_dict = parse_yaml(input_file)
    return yaml_dict


def find_downloaded_file(file_type):
    download_folder = cnf.DOWNLOAD_PATH
    extensions = {
        "description": [".description"],
        "image": [".webp", ".jpg"],
        "video": [".mp4"],
    }
    for ext in extensions[file_type]:
        file = glob(download_folder + "*" + ext)
        if file:
            return file[0]
    logger.error("No {} file found.".format(file_type))
    return None


def get_downloaded_files_dict():
    new_files = {}
    file_types = ["description", "image", "video"]
    for ft in file_types:
        new_files[ft] = find_downloaded_file(ft)
        if not new_files[ft]:
            logger.error("Unable to find {} file".format(ft))
    return new_files


def create_audio_file(video_file):
    if not video_file:
        logger.error("No video file string found!")
        return ""
    source_mp4 = Path(video_file)
    target_mp3 = source_mp4.with_suffix(".mp3")
    if target_mp3.exists():
        logger.debug("Audio file {} already exists.  Skipping".format(str(target_mp3)))
    else:
        args = [
            "ffmpeg",
            "-n",
            "-i",
            source_mp4,
            "-hide_banner",
            "-loglevel",
            "warning",
            target_mp3,
        ]
        ffmpeg = subprocess.run(args)
        if ffmpeg.returncode:
            print(f"FFMPEG returned: {ffmpeg.returncode}.  Quitting")
            return None
    return str(target_mp3)


def compute_source_file_paths(source, source_root_path, files):
    final_paths = {}
    for file_type, file in files.items():
        file_name = Path(file).name
        if file_type == "audio":
            sub_path = "/audio/Harry Mack/"
        else:
            sub_path = "/video/Harry Mack/"

        final_paths[file_type] = str(
            Path(source_root_path + sub_path + source.collection_name + "/" + file_name)
        )
    return final_paths


def verify_files_exist():

    # i built this to verify source repo files only
    # and later expanded it to be more generic
    # should probably move to a different file
    file_models = [crud.SourceFileRepo, crud.TrackFileRepo]
    logger.info("Checking that all files listed in db exist on disk")
    for fm in file_models:

        session = db_session()
        file_list = fm.fetchAll(session)
        session.close
        for file in file_list:
            my_file = Path(file.file_name)
            if not my_file.is_file():
                logger.error("This file doesn't exist {}".format(file.file_name))


def download_sources():
    session = db_session()
    sources = crud.SourceRepo.fetchNotDownloaded(session=session).all()
    session.close()
    if len(sources) == 0:
        logger.info("No new videos to download")
        return None

    # this is the root path where the new files will be
    source_root_path = cnf.SOURCE_ROOT_PATH

    file_types = ["audio", "description", "image", "video"]

    for source in sources:
        dl = download_files(source.url, source.filename_base)
        if not dl:
            logger.error(
                "There was a problem downloading this video {}".format(
                    source.filename_base
                )
            )
        downloaded_files = get_downloaded_files_dict()
        downloaded_files["audio"] = create_audio_file(downloaded_files["video"])
        final_files = compute_source_file_paths(
            source, source_root_path, downloaded_files
        )

        for ft in file_types:
            if move_file(downloaded_files[ft], final_files[ft]):
                new_file_object = {
                    "file_name": final_files[ft],
                    "file_type": ft,
                    "source_id": source.id,
                }
                source_file_schema = schemas.SourceFileSchema(**new_file_object)
                source_file_model = models.SourceFile(**source_file_schema.dict())

                session = db_session()
                crud.SourceFileRepo.create(db_object=source_file_model, session=session)
                session.close()


def update_sources_in_db():

    individual_videos = parse_individual_videos()
    add_collections_to_db(individual_videos)
    add_individual_video_to_db(individual_videos)
    add_rest_of_videos_to_db()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    update_sources_in_db()
    download_sources()
