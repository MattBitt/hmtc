import os
import csv

from configs import cnf
from my_logging import logger
from utils import convert_hms_to_ms
import crud
import models
import schemas
from db import db_session, Base, engine


def is_track_in_db(track_title):
    session = db_session()
    track = crud.TrackRepo.fetchByTrackTitle(track_title, session)
    session.close()
    return track is not None


def add_track_to_db(source_dict):
    model = models.Track
    repo = crud.TrackRepo
    schema = schemas.TrackBaseSchema
    logger.debug("Adding new track to database {}".format(track_dict["track_title"]))
    add_to_db(track_dict, model, repo, schema)


def add_to_db(data_to_add, model, repo, schema):
    data = schema(**data_to_add)
    data_model = model(**data.dict())
    session = db_session()
    repo.create(data_model, session)
    session.close()
    return 201


def import_tracks_from_csv():
    csv_name = cnf.APP_CONFIG.csv_to_import
    if not os.path.exists(csv_name):
        raise FileNotFoundError(f"File {csv_name} not found")

    with open(csv_name, "r") as f:
        csv_reader = csv.DictReader(f)
        track_info = list(csv_reader)
    return track_info


def compute_full_title(track, source, album):
    final_track_title = ""

    # if there is a prefix, title should look like OB 004.1 drinkin, on a sunday, high as fuck
    if album.track_prefix:
        episode_number = source.filename_base[-3:]

        final_track_title = (
            album.track_prefix
            + " "
            + episode_number
            + "."
            + track["track_number"]
            + " "
        )

    final_track_title = final_track_title + track["title"]

    return final_track_title


def find_source_and_album_id(url):
    session = db_session()
    source = crud.SourceRepo.fetchByURL(url=url, session=session)
    album = crud.AlbumRepo.fetchById(id=source.album.id, session=session)
    session.close()
    return source, album


def create_track_dict(track):
    required_keys = ["title", "start_time", "end_time", "url"]
    for k in required_keys:
        if k not in track:
            logger.error("Invalid track {} is missing {}".format(track["title"], k))

    start_time_ms = convert_hms_to_ms(track["start_time"])
    end_time_ms = convert_hms_to_ms(track["end_time"])
    source, album = find_source_and_album_id(track["url"])
    session = db_session()

    track_number = str(
        crud.TrackRepo.fetchTrackCountByAlbum(album_id=album.id, session=session) + 1
    ).zfill(2)
    session.close()
    track["track_number"] = track_number

    full_title = compute_full_title(track, source, album)

    track_dict = {
        "track_title": full_title,
        "start_time": start_time_ms,
        "end_time": end_time_ms,
        "source_id": source.id,
        "album_id": album.id,
        "track_number": track_number,
    }
    return track_dict


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    tracks = import_tracks_from_csv()
    for track in tracks:
        if not is_track_in_db(track["title"]):
            track_dict = create_track_dict(track)
            add_track_to_db(track_dict)
