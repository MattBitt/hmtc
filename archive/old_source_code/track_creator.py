from pathlib import Path
import subprocess

from db import Base, engine, db_session
import crud
import models
import schemas
from my_logging import logger
import eyed3
from utils import convert_ms_to_hms


def get_source_audio_file(source):
    for file in source.files:
        if file.file_type == "audio":
            return file.file_name
    logger.error("No file found for source: {}".format(source))
    return None


def create_mp3_from_source(track):
    source_file = Path(get_source_audio_file(track.source))
    if str(track.start_time) == str(track.end_time):
        logger.error(
            "Start time and end time are the the same for track: {}", track.track_title
        )
        raise IndexError
    elif track.end_time < track.start_time:
        logger.error(
            "The end time is before the start time  for track: {} - {}",
            track.id,
            track.track_title,
        )
        raise IndexError
    album_folder = Path(track.album.path + track.album.album_name)
    album_folder.mkdir(exist_ok=True)
    start_time = convert_ms_to_hms(track.start_time)
    end_time = convert_ms_to_hms(track.end_time)
    final_track_file = album_folder / str(
        str(track.track_number) + " - " + track.track_title + ".mp3"
    )
    if final_track_file.exists():
        # logger.debug("Destination file already exits {}".format(final_track_file))
        # if i want to overwrite, i would do it here
        pass
    else:
        logger.debug(
            "About to exterct mp3 from source for {}".format(track.track_title)
        )
        args = [
            "ffmpeg",
            "-n",
            "-i",
            str(source_file),
            "-ss",
            start_time,
            "-to",
            end_time,
            "-hide_banner",
            "-loglevel",
            "warning",
            str(final_track_file),
        ]
        ffmpeg = subprocess.run(args)
        if ffmpeg.returncode:
            logger.error("FFMPEG returned: {}.  Quitting".format(ffmpeg.returncode))
            return None

    new_file_object = {
        "file_name": str(final_track_file),
        "file_type": "audio",
        "track_id": track.id,
    }

    track_file_schema = schemas.TrackFileSchema(**new_file_object)
    track_file_model = models.TrackFile(**track_file_schema.dict())

    session = db_session()
    file_exists = crud.TrackFileRepo.fetch_by(
        session=session, filter={"file_name": str(final_track_file)}
    )

    if not file_exists:
        crud.TrackFileRepo.create(db_object=track_file_model, session=session)

    session.close()


def write_id3_tags(track_id) -> None:
    session = db_session()
    track = crud.TrackRepo.fetchById(id=track_id, session=session)
    if track:
        audiofile = eyed3.load(track.files[0].file_name)
        if audiofile is not None and audiofile.tag is not None:
            # need to fix this later to reflect actual artists
            audiofile.tag.artist = "Harry Mack"
            audiofile.tag.album_artist = "Harry Mack"

            audiofile.tag.album = track.album.album_name
            audiofile.tag.title = track.track_title
            audiofile.tag.track_num = track.track_number
            image_file = crud.SourceFileRepo.fetch_by(
                session=session,
                filter={"source_id": track.source.id, "file_type": "image"},
            ).file_name
            with open(image_file, "rb") as f:
                imagedata = f.read()
                audiofile.tag.images.set(3, imagedata, "image/jpeg", "")
            audiofile.tag.recording_date = str(track.source.upload_date)
            audiofile.tag.save()
    else:
        logger.error("No track found for track_id {}".format(str(track_id)))
    session.close()


def create_all_tracks():
    # this function will search the db for tracks without any
    # existing file.  it should then loop through and create them
    # from each source
    session = db_session()
    tracks = crud.TrackRepo.fetch_items_with_no_files(session=session).all()
    for track in tracks:
        try:
            create_mp3_from_source(track)
            # this should be a separate task from writing the mp3 files
            write_id3_tags(track.id)
        except Exception:
            raise
    session.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    create_all_tracks()
