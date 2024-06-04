from typing import List

import crud
import models
from db import get_session
from fastapi import APIRouter, Depends, HTTPException
from my_logging import logger
from plex_functions import currently_playing
from schemas import (
    AlbumBaseSchema,
    AlbumSchema,
    AlbumWithRelationships,
    ArtistBaseSchema,
    ArtistSchema,
    BeatBaseSchema,
    BeatSchema,
    ProducerBaseSchema,
    ProducerSchema,
    SourceSchema,
    SourceWithRelationships,
    TagBaseSchema,
    TagSchema,
    TrackBaseSchema,
    TrackSchema,
    TrackWithRelationships,
    WhatsPlayingSchema,
    WordBaseSchema,
    WordSchema,
    WordWithRelationships,
)
from sqlalchemy.orm import Session

source_router = APIRouter(prefix="/sources", tags=["Sources"])
track_router = APIRouter(prefix="/tracks", tags=["Tracks"])
album_router = APIRouter(prefix="/albums", tags=["Albums"])
word_router = APIRouter(prefix="/words", tags=["Words"])
producer_router = APIRouter(prefix="/producers", tags=["Producers"])
tag_router = APIRouter(prefix="/tags", tags=["Tags"])
beat_router = APIRouter(prefix="/beats", tags=["Beats"])
artist_router = APIRouter(prefix="/artists", tags=["Artists"])
whatsplaying_router = APIRouter(prefix="/whatsplaying", tags=["Whats Playing"])


@source_router.get("/", response_model=List[SourceSchema])
def read_sources(session: Session = Depends(get_session)):

    sources = crud.SourceRepo.fetchNotIgnored(session=session).all()
    logger.debug("Getting all sources")
    return sources


@source_router.get("/recent", response_model=List[SourceWithRelationships])
def read_recent_sources(session: Session = Depends(get_session)):
    sources = crud.SourceRepo.fetchRecent(session=session)
    logger.debug("Getting recent sources")
    return sources


@source_router.get("/{id}", response_model=SourceWithRelationships)
def read_source(id: int, session: Session = Depends(get_session)):
    source = crud.SourceRepo.fetchById(session=session, id=id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


# @source_router.post("/", response_model=SourceSchema)
# def create_source(source: SourceBaseSchema, session: Session = Depends(get_session)):
#     # album_id = get_or_create_album(source, session)
#     # I don't think this w
#     source_model = models.Source(**source.dict())
#     source_model.album_id = album_id
#     source = crud.SourceRepo.create(db_object=source_model, session=session)
#     return source


# this should probably go away.  will i ever be creating sources/albums from post requests?
# they should typically be created by the auto-parser
# def get_or_create_album(source: SourceBaseSchema, session: Session):
#     album_data = {}
#     if source.separate_album_per_video and source.episode_number:
#         album_data["album_name"] = source.video_type + " " + source.episode_number
#     else:
#         album_data["album_name"] = source.video_type
#     album_data["track_prefix"] = "My Prefix:  "
#     album_data["path"] = "some/random/path/"
#     # check if album already exists
#     album = crud.AlbumRepo.fetchByAlbumName(
#         album_name=album_data["album_name"], session=session
#     )
#     if not album:
#         album_schema = AlbumBaseSchema(**album_data)
#         album_model = models.Album(**album_schema.dict())
#         album = crud.AlbumRepo.create(db_object=album_model, session=session)
#     return album.id


@source_router.put("/{id}", response_model=SourceSchema)
def update_source(source: SourceSchema, session: Session = Depends(get_session)):

    updated_source = crud.SourceRepo.fetchById(id=source.id, session=session)
    if updated_source:
        updated_source.video_title = source.video_title
        updated_source.url = source.url
        # TODO update all fields
        source = crud.SourceRepo.update(db_object=updated_source, session=session)
        source = crud.SourceRepo.fetchById(id=updated_source.id, session=session)
        return source
    return {"message": "source not found"}, 404


@source_router.delete("/{id}")
def delete_source(id: int, session: Session = Depends(get_session)):
    source_data = crud.SourceRepo.fetchById(id=id, session=session)
    if source_data:
        crud.SourceRepo.delete(id=id, session=session)
        return {"message": "source deleted successfully"}, 200
    return {"message": "source not found"}, 404

    # ******************************** SOURCE ROUTER *************************


# ******************************** TRACK ROUTER *************************
# These functions are called from the front end
# either nothing or an id is sent by the front end
# this data is sent (along with db session) to the db functions
@track_router.get("/", response_model=List[TrackSchema])
def read_tracks(session: Session = Depends(get_session)):
    # remove the limit when testing is finished
    tracks = crud.TrackRepo.fetchAll(session=session)
    return tracks


@track_router.get("/{id}", response_model=TrackWithRelationships)
def read_track(id: int, session: Session = Depends(get_session)):
    track = crud.TrackRepo.fetchById(session=session, id=id)
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


@track_router.post("/", response_model=TrackWithRelationships)
def create_track(
    track: TrackBaseSchema,
    words: List[WordBaseSchema],
    tags: List[TagBaseSchema],
    producers: List[ProducerBaseSchema],
    beats: List[BeatBaseSchema],
    session: Session = Depends(get_session),
):
    logger.debug("track input:  {}".format(track))
    word_list = create_word_list(words, session)
    tag_list = create_tag_list(tags, session)
    producer_list = create_producer_list(producers, session)
    beat_list = create_beat_list(beats, session)

    track_model = models.Track(**track.dict())
    # need to find album from source
    source = crud.SourceRepo.fetchById(id=track.source_id, session=session)
    track_model.album_id = source.album.id
    # after that need to calculate track number

    track = crud.TrackRepo.create(db_object=track_model, session=session)

    track = add_words_to_track(track, word_list, session)
    track = add_tags_to_track(track, tag_list, session)
    track = add_producers_to_track(track, producer_list, session)
    track = add_beats_to_track(track, beat_list, session)
    track = TrackWithRelationships.from_orm(track)
    return track


def create_word_list(words: List[WordBaseSchema], session: Session):
    word_list = []
    for word in words:
        new_word = get_or_create_word(word, session)
        word_list.append(new_word)
    return word_list


def create_tag_list(tags: List[TagBaseSchema], session: Session):
    tag_list = []
    for tag in tags:
        new_tag = get_or_create_tag(tag, session)
        tag_list.append(new_tag)
    return tag_list


def create_producer_list(producers: List[ProducerBaseSchema], session: Session):
    producer_list = []
    for producer in producers:
        new_producer = get_or_create_producer(producer, session)
        producer_list.append(new_producer)
    return producer_list


def create_beat_list(beats: List[BeatBaseSchema], session: Session):
    beat_list = []
    for beat in beats:
        new_beat = get_or_create_beat(beat, session)
        beat_list.append(new_beat)
    return beat_list


def get_or_create_word(word: WordBaseSchema, session: Session) -> models.Word:
    new_word = crud.WordRepo.fetchByWord(word=word.word, session=session)
    if new_word:
        return new_word
    else:
        word_model = models.Word(**word.dict())
        new_word = crud.WordRepo.create(db_object=word_model, session=session)
        return new_word


def get_or_create_tag(tag: TagBaseSchema, session: Session) -> models.Tag:
    new_tag = crud.TagRepo.fetchByTag(tag=tag.tag, session=session)
    if new_tag:
        return new_tag
    else:
        tag_model = models.Tag(**tag.dict())
        new_tag = crud.TagRepo.create(db_object=tag_model, session=session)
        return new_tag


def get_or_create_beat(beat: BeatBaseSchema, session: Session) -> models.Beat:
    new_beat = crud.BeatRepo.fetchByBeat(beat=beat.beat_name, session=session)
    if new_beat:
        return new_beat
    else:
        beat_model = models.Beat(**beat.dict())
        new_beat = crud.BeatRepo.create(db_object=beat_model, session=session)
        return new_beat


def get_or_create_producer(
    producer: ProducerBaseSchema, session: Session
) -> models.Producer:
    new_producer = crud.ProducerRepo.fetchByProducer(
        producer=producer.producer, session=session
    )
    if new_producer:
        return new_producer
    else:
        producer_model = models.Producer(**producer.dict())
        new_producer = crud.ProducerRepo.create(
            db_object=producer_model, session=session
        )
        return new_producer


def add_words_to_track(
    track: models.Track, words: List[models.Word], session: Session
) -> TrackBaseSchema:
    for word in words:
        if word and word not in track.words:
            next_word_sequence_number = (
                crud.TrackWordRepo().fetchLastWordSequence(track, session) + 1
            )
            track_word = models.TrackWord(
                track_id=track.id,
                word_id=word.id,
                index=next_word_sequence_number,
            )
            session.add_all([track, track_word])
            session.commit()

    return track


def add_tags_to_track(
    track: models.Track, tags: List[models.Tag], session: Session
) -> TrackBaseSchema:
    for tag in tags:
        if tag and tag not in track.tags:
            next_tag_sequence_number = (
                crud.TrackTagRepo().fetchLastTagSequence(track, session) + 1
            )
            track_tag = models.TrackTag(
                track_id=track.id,
                tag_id=tag.id,
                sequence_order=next_tag_sequence_number,
            )
            session.add_all([track, track_tag])
            session.commit()

    return track


def add_beats_to_track(
    track: models.Track, beats: List[models.Beat], session: Session
) -> TrackBaseSchema:
    for beat in beats:
        if beat and beat not in track.beats:
            next_beat_sequence_number = (
                crud.TrackBeatRepo().fetchLastBeatSequence(track, session) + 1
            )
            track_beat = models.TrackBeat(
                track_id=track.id,
                beat_id=beat.id,
                sequence_order=next_beat_sequence_number,
            )
            session.add_all([track, track_beat])
            session.commit()

    return track


def add_producers_to_track(
    track: models.Track, producers: List[models.Producer], session: Session
) -> TrackBaseSchema:
    for producer in producers:
        if producer and producer not in track.producers:
            next_producer_sequence_number = (
                crud.TrackProducerRepo().fetchLastProducerSequence(track, session) + 1
            )
            track_producer = models.TrackProducer(
                track_id=track.id,
                producer_id=producer.id,
                sequence_order=next_producer_sequence_number,
            )
            session.add_all([track, track_producer])
            session.commit()

    return track


@track_router.put("/{id}", response_model=TrackSchema)
def update_track(track: TrackSchema, session: Session = Depends(get_session)):
    updated_track = crud.TrackRepo.fetchById(id=track.id, session=session)
    if updated_track:
        updated_track.track_title = track.track_title
        updated_track.start_time = track.start_time
        updated_track.end_time = track.end_time
        updated_track.plex_id = track.plex_id
        updated_track.track_number = track.track_number
        track = crud.TrackRepo.update(db_object=updated_track, session=session)
        track = crud.TrackRepo.fetchById(id=updated_track.id, session=session)
        return track
    return {"message": "track not found"}, 404


@track_router.delete("/{id}")
def delete_track(id: int, session: Session = Depends(get_session)):
    track_data = crud.TrackRepo.fetchById(id=id, session=session)
    if track_data:
        crud.TrackRepo.delete(id=id, session=session)
        return {"message": "track deleted successfully"}, 200
    return {"message": "track not found"}, 404

    # ******************************** TRACK ROUTER *************************


# ******************************** ALBUM ROUTER *************************
# These functions are called from the front end
# either nothing or an id is sent by the front end
# this data is sent (along with db session) to the db functions
@album_router.get("/", response_model=List[AlbumWithRelationships])
def read_albums(session: Session = Depends(get_session)):
    albums = crud.AlbumRepo.fetchAll(session=session)
    return albums


@album_router.get("/{id}", response_model=AlbumWithRelationships)
def read_album(id: int, session: Session = Depends(get_session)):
    album = crud.AlbumRepo.fetchById(session=session, id=id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


@album_router.get("/{id}/next_track_number")
def next_track_number(id: int, session: Session = Depends(get_session)):
    track_number = (
        crud.AlbumRepo.fetchTrackCountByAlbum(session=session, album_id=id) + 1
    )
    if track_number == 1:
        raise HTTPException(status_code=404, detail="Album not found")
    return track_number


@album_router.post("/", response_model=AlbumSchema)
def create_album(album: AlbumBaseSchema, session: Session = Depends(get_session)):
    album_model = models.Album(**album.dict())
    album = crud.AlbumRepo.create(db_object=album_model, session=session)
    return album


@album_router.put("/{id}", response_model=AlbumSchema)
def update_album(album: AlbumSchema, session: Session = Depends(get_session)):
    updated_album = crud.AlbumRepo.fetchById(id=album.id, session=session)
    if updated_album:
        updated_album.album_name = album.album_name
        updated_album.path = album.path
        updated_album.track_prefix = album.track_prefix
        album = crud.AlbumRepo.update(db_object=updated_album, session=session)
        album = crud.AlbumRepo.fetchById(id=updated_album.id, session=session)
        return album
    return {"message": "album not found"}, 404


@album_router.delete("/{id}")
def delete_album(id: int, session: Session = Depends(get_session)):
    album_data = crud.AlbumRepo.fetchById(id=id, session=session)
    if album_data:
        crud.AlbumRepo.delete(id=id, session=session)
        return {"message": "album deleted successfully"}, 200
    return {"message": "album not found"}, 404


# ******************************** ALBUM ROUTER *************************


# ******************************** WORD ROUTER *************************
# These functions are called from the front end
# either nothing or an id is sent by the front end
# this data is sent (along with db session) to the db functions
@word_router.get("/", response_model=List[WordSchema])
def read_words(session: Session = Depends(get_session)):
    words = crud.WordRepo.fetchAll(session=session)
    return words


@word_router.get("/fake")
def read_fake_words(session: Session = Depends(get_session)):
    # words = crud.WordRepo.fetchAll(session=session)
    words = [
        {"label": "dictionary", "value": "dictionary"},
        {"label": "book", "value": "book"},
        {"label": "table", "value": "table"},
        {"label": "bedside", "value": "bedside"},
        {"label": "precautionary", "value": "precautionary"},
    ]

    return words


@word_router.get("/{id}", response_model=WordWithRelationships)
def read_word(id: int, session: Session = Depends(get_session)):
    word = crud.WordRepo.fetchById(session=session, id=id)
    if word is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


@word_router.post("/", response_model=WordSchema)
def create_word(word: WordBaseSchema, session: Session = Depends(get_session)):
    word_model = models.Word(**word.dict())
    word = crud.WordRepo.create(db_object=word_model, session=session)
    return word


@word_router.put("/{id}", response_model=WordSchema)
def update_word(word: WordSchema, session: Session = Depends(get_session)):
    updated_word = crud.WordRepo.fetchById(id=word.id, session=session)
    if updated_word:
        updated_word.word = word.word
        word = crud.WordRepo.update(db_object=updated_word, session=session)
        word = crud.WordRepo.fetchById(id=updated_word.id, session=session)
        return word
    return {"message": "word not found"}, 404


@word_router.delete("/{id}")
def delete_word(id: int, session: Session = Depends(get_session)):
    word_data = crud.WordRepo.fetchById(id=id, session=session)
    if word_data:
        crud.WordRepo.delete(id=id, session=session)
        return {"message": "word deleted successfully"}, 200
    return {"message": "word not found"}, 404


# ******************************** WORD ROUTER *************************


# ******************************** PRODUCER ROUTER *************************
# These functions are called from the front end
# either nothing or an id is sent by the front end
# this data is sent (along with db session) to the db functions
@producer_router.get("/", response_model=List[ProducerSchema])
def read_producers(session: Session = Depends(get_session)):
    producers = crud.ProducerRepo.fetchAll(session=session)
    return producers


@producer_router.get("/{id}", response_model=ProducerSchema)
def read_producer(id: int, session: Session = Depends(get_session)):
    producer = crud.ProducerRepo.fetchById(session=session, id=id)
    if producer is None:
        raise HTTPException(status_code=404, detail="Producer not found")
    return producer


@producer_router.post("/", response_model=ProducerSchema)
def create_producer(
    producer: ProducerBaseSchema, session: Session = Depends(get_session)
):
    producer_model = models.Producer(**producer.dict())
    producer = crud.ProducerRepo.create(
        db_object=producer_model,
        session=session,
    )
    return producer


@producer_router.put("/{id}", response_model=ProducerSchema)
def update_producer(producer: ProducerSchema, session: Session = Depends(get_session)):
    updated_producer = crud.ProducerRepo.fetchById(id=producer.id, session=session)
    if updated_producer:
        updated_producer.producer = producer.producer
        producer = crud.ProducerRepo.update(db_object=updated_producer, session=session)
        producer = crud.ProducerRepo.fetchById(id=updated_producer.id, session=session)
        return producer
    return {"message": "producer not found"}, 404


@producer_router.delete("/{id}")
def delete_producer(id: int, session: Session = Depends(get_session)):
    producer_data = crud.ProducerRepo.fetchById(id=id, session=session)
    if producer_data:
        crud.ProducerRepo.delete(id=id, session=session)
        return {"message": "producer deleted successfully"}, 200
    return {"message": "producer not found"}, 404


# ******************************** PRODUCER ROUTER *************************


# ******************************** TAG ROUTER *************************
# These functions are called from the front end
# either nothing or an id is sent by the front end
# this data is sent (along with db session) to the db functions
@tag_router.get("/", response_model=List[TagSchema])
def read_tags(session: Session = Depends(get_session)):
    tags = crud.TagRepo.fetchAll(session=session)
    return tags


@tag_router.get("/{id}", response_model=TagSchema)
def read_tag(id: int, session: Session = Depends(get_session)):
    tag = crud.TagRepo.fetchById(session=session, id=id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@tag_router.post("/", response_model=TagSchema)
def create_tag(tag: TagBaseSchema, session: Session = Depends(get_session)):
    tag_model = models.Tag(**tag.dict())
    tag = crud.TagRepo.create(db_object=tag_model, session=session)
    return tag


@tag_router.put("/{id}", response_model=TagSchema)
def update_tag(tag: TagSchema, session: Session = Depends(get_session)):
    updated_tag = crud.TagRepo.fetchById(id=tag.id, session=session)
    if updated_tag:
        updated_tag.tag = tag.tag
        tag = crud.TagRepo.update(db_object=updated_tag, session=session)
        tag = crud.TagRepo.fetchById(id=updated_tag.id, session=session)
        return tag
    return {"message": "tag not found"}, 404


@tag_router.delete("/{id}")
def delete_tag(id: int, session: Session = Depends(get_session)):
    tag_data = crud.TagRepo.fetchById(id=id, session=session)
    if tag_data:
        crud.TagRepo.delete(id=id, session=session)
        return {"message": "tag deleted successfully"}, 200
    return {"message": "tag not found"}, 404


# ******************************** TAG ROUTER *************************


# ******************************** BEAT ROUTER *************************
# These functions are called from the front end
# either nothing or an id is sent by the front end
# this data is sent (along with db session) to the db functions
@beat_router.get("/", response_model=List[BeatSchema])
def read_beats(session: Session = Depends(get_session)):
    beats = crud.BeatRepo.fetchAll(session=session)
    return beats


@beat_router.get("/{id}", response_model=BeatSchema)
def read_beat(id: int, session: Session = Depends(get_session)):
    beat = crud.BeatRepo.fetchById(session=session, id=id)
    if beat is None:
        raise HTTPException(status_code=404, detail="Beat not found")
    return beat


@beat_router.post("/", response_model=BeatSchema)
def create_beat(beat: BeatBaseSchema, session: Session = Depends(get_session)):
    beat_model = models.Beat(**beat.dict())
    beat = crud.BeatRepo.create(db_object=beat_model, session=session)
    return beat


@beat_router.put("/{id}", response_model=BeatSchema)
def update_beat(beat: BeatSchema, session: Session = Depends(get_session)):
    updated_beat = crud.BeatRepo.fetchById(id=beat.id, session=session)
    if updated_beat:
        updated_beat.beat_name = beat.beat_name
        beat = crud.BeatRepo.update(db_object=updated_beat, session=session)
        beat = crud.BeatRepo.fetchById(id=updated_beat.id, session=session)
        return beat
    return {"message": "beat not found"}, 404


@beat_router.delete("/{id}")
def delete_beat(id: int, session: Session = Depends(get_session)):
    beat_data = crud.BeatRepo.fetchById(id=id, session=session)
    if beat_data:
        crud.BeatRepo.delete(id=id, session=session)
        return {"message": "beat deleted successfully"}, 200
    return {"message": "beat not found"}, 404


# ******************************** BEAT ROUTER *************************


# ******************************** ARTIST ROUTER *************************
# These functions are called from the front end
# either nothing or an id is sent by the front end
# this data is sent (along with db session) to the db functions
@artist_router.get("/", response_model=List[ArtistSchema])
def read_artists(session: Session = Depends(get_session)):
    artists = crud.ArtistRepo.fetchAll(session=session)
    return artists


@artist_router.get("/{id}", response_model=ArtistSchema)
def read_artist(id: int, session: Session = Depends(get_session)):
    artist = crud.ArtistRepo.fetchById(session=session, id=id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@artist_router.post("/", response_model=ArtistSchema)
def create_artist(artist: ArtistBaseSchema, session: Session = Depends(get_session)):
    artist_model = models.Artist(**artist.dict())
    artist = crud.ArtistRepo.create(db_object=artist_model, session=session)
    return artist


@artist_router.put("/{id}", response_model=ArtistSchema)
def update_artist(artist: ArtistSchema, session: Session = Depends(get_session)):
    updated_artist = crud.ArtistRepo.fetchById(id=artist.id, session=session)
    if updated_artist:
        updated_artist.artist = artist.artist
        artist = crud.ArtistRepo.update(db_object=updated_artist, session=session)
        artist = crud.ArtistRepo.fetchById(id=updated_artist.id, session=session)
        return artist
    return {"message": "artist not found"}, 404


@artist_router.delete("/{id}")
def delete_artist(id: int, session: Session = Depends(get_session)):
    artist_data = crud.ArtistRepo.fetchById(id=id, session=session)
    if artist_data:
        crud.ArtistRepo.delete(id=id, session=session)
        return {"message": "artist deleted successfully"}, 200
    return {"message": "artist not found"}, 404


# ******************************** ARTIST ROUTER *************************


@whatsplaying_router.get("/", response_model=WhatsPlayingSchema)
def get_whats_playing(session: Session = Depends(get_session)):
    # query plex api for whats playing
    # determine if it is a source or a track
    # query the appropriate table for record
    logger.debug("About to fetch whats playing from Plex")
    whatsplaying = currently_playing()

    # need to figure out how to work with multiple playing at once
    # for now just use first result
    whatsplaying = whatsplaying[0]
    if whatsplaying["library_type"] == "source":
        media_type = "source"
        file_model = crud.SourceFileRepo
        model = crud.SourceRepo
        current_time = whatsplaying["current_time"]
    elif whatsplaying["library_type"] == "track":
        media_type = "track"
        file_model = crud.TrackFileRepo
        model = crud.TrackRepo
        current_time = whatsplaying["current_time"]
    else:
        raise HTTPException(
            status_code=404, detail="No media currently found playing on Plex"
        )

    playing = file_model.fetch_item_with_file_name(
        whatsplaying["video_file"], session=session
    )
    if playing:
        media_info = model.fetchById(id=playing[0].source_id, session=session)
    else:
        raise HTTPException(
            status_code=404,
            detail="No file found to match {}".format(whatsplaying["video_file"]),
        )
    return {
        "media_type": media_type,
        "current_time": current_time,
        "media_info": media_info,
    }
