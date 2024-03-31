from sqlalchemy.orm import Session
from models import (
    Base,
    Source,
    Track,
    Album,
    Artist,
    Word,
    Producer,
    Tag,
    TrackWord,
    TrackTag,
    TrackProducer,
    TrackBeat,
    TrackArtist,
    Beat,
    SourceFile,
    AlbumFile,
    TrackFile,
)


class DBOperations:
    def __init__(self, object_type):
        self.object_type = object_type

    def create(self, db_object, session: Session) -> Base:
        session.add(db_object)
        session.commit()
        return db_object

    def fetchById(self, id: int, session: Session):
        return session.query(self.object_type).filter_by(id=id).first()

    def fetchByURL(self, url: str, session):
        return session.query(self.object_type).filter_by(url=url).first()

    def fetchURLs(self, session):
        results = session.query(self.object_type.url).all()
        url_list = results = [r for (r,) in results]
        return url_list

    def fetchNotDownloaded(self, session: Session):
        # returns all sources that are not ignored and that don't have any matching file records
        q = session.query(Source).where(Source.ignore.is_(False))
        return q.filter(~Source.files.any())

    def fetch_items_with_no_files(self, session: Session):
        return session.query(self.object_type).filter(~self.object_type.files.any())

    def fetch_item_with_file_name(self, file_name: str, session: Session):
        return session.query(self.object_type).filter_by(file_name=file_name).all()

    def fetchCountByAlbum(self, album_id: int, session: Session):
        return session.query(self.object_type).filter_by(album_id=album_id).count()

    def fetchTrackCountByAlbum(self, album_id: int, session: Session):
        return session.query(Track).filter_by(album_id=album_id).count()

    def fetchByAlbumName(self, album_name: str, session: Session):
        return session.query(self.object_type).filter_by(album_name=album_name).first()

    def fetchByArtist(self, artist: str, session: Session):
        return session.query(Artist).filter_by(artist_name=artist).first()

    def fetchByBeat(self, beat: str, session: Session):
        return session.query(Beat).filter_by(beat_name=beat).first()

    def fetchByProducer(self, producer: str, session: Session):
        return session.query(Producer).filter_by(producer=producer).first()

    def fetchByTrackTitle(self, track_title: str, session: Session):
        return (
            session.query(Track).filter(Track.track_title.contains(track_title)).first()
        )

    def fetch_by(self, session: Session = None, filter=None):
        return session.query(self.object_type).filter_by(**filter).first()

    def fetchByWord(self, word: str, session: Session):
        return session.query(Word).filter_by(word=word).first()

    def fetchByTag(self, tag: str, session: Session):
        return session.query(Tag).filter_by(tag=tag).first()

    def fetchAll(self, session: Session):
        # remove the limit when testing is finished
        return session.query(self.object_type).all()

    def fetchNotIgnored(self, session: Session):

        return session.query(self.object_type).filter_by(ignore=False)

    def fetchIgnored(self, session: Session):
        return session.query(self.object_type).filter_by(ignore=True)

    def fetchWords(self, track_id, session: Session):
        track = session.query(self.object_type).filter_by(id=track_id).first()
        return track.words

    def fetchRecent(self, session: Session):
        return (
            # session.query(self.object_type)
            self.fetchNotIgnored(session)
            .order_by(self.object_type.created.desc())
            .limit(10)
            .all()
        )

    def delete(self, id: int, session: Session) -> None:
        db_object = session.query(self.object_type).filter_by(id=id).first()
        session.delete(db_object)
        session.commit()

    def update(
        self,
        db_object,
        session: Session,
    ):
        session.merge(db_object)
        session.commit()

    def bulk_create(self, session: Session, objects_list):
        session.bulk_save_objects(objects_list)
        session.commit()

    def bulk_delete(self, session: Session):
        session.query(self.object_type).delete()
        session.commit()

    def count_rows(self, session: Session):
        return session.query(self.object_type).count()


SourceRepo = DBOperations(Source)
TrackRepo = DBOperations(Track)
AlbumRepo = DBOperations(Album)
WordRepo = DBOperations(Word)
ProducerRepo = DBOperations(Producer)
BeatRepo = DBOperations(Beat)
ArtistRepo = DBOperations(Artist)
TagRepo = DBOperations(Tag)
SourceFileRepo = DBOperations(SourceFile)
AlbumFileRepo = DBOperations(AlbumFile)
TrackFileRepo = DBOperations(TrackFile)


class TrackWordRepo:
    def fetchLastWordSequence(self, track: Track, session: Session):
        # words = session.query(Track).join(TrackWord, Track.words).all()
        words = session.query(TrackWord).filter(TrackWord.track_id == track.id).all()
        return len(words)


class TrackTagRepo:
    def fetchLastTagSequence(self, track: Track, session: Session):
        # words = session.query(Track).join(TrackWord, Track.words).all()
        tags = session.query(TrackTag).filter(TrackTag.track_id == track.id).all()
        return len(tags)


class TrackProducerRepo:
    def fetchLastProducerSequence(self, track: Track, session: Session):
        # words = session.query(Track).join(TrackWord, Track.words).all()
        producers = (
            session.query(TrackProducer)
            .filter(TrackProducer.track_id == track.id)
            .all()
        )
        return len(producers)


class TrackBeatRepo:
    def fetchLastBeatSequence(self, track: Track, session: Session):
        # words = session.query(Track).join(TrackWord, Track.words).all()
        beats = session.query(TrackBeat).filter(TrackBeat.track_id == track.id).all()
        return len(beats)


class TrackArtistRepo:
    def fetchLastArtistSequence(self, track: Track, session: Session):
        # words = session.query(Track).join(TrackWord, Track.words).all()
        artists = (
            session.query(TrackArtist).filter(TrackArtist.track_id == track.id).all()
        )
        return len(artists)
