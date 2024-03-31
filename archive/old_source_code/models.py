from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)  # type ignore
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

# from sqlalchemy.ext.associationproxy import association_proxy
from db import Base


class CommonModel(object):
    id = Column(Integer, primary_key=True)

    @declared_attr
    def created(cls):
        return Column(DateTime(timezone=True), server_default=func.now())

    @declared_attr
    def modified(cls):
        return Column(DateTime(timezone=True), onupdate=func.now())


class Source(Base, CommonModel):  # type: ignore
    __tablename__ = "sources"
    # Required
    url = Column(String(80), nullable=False)
    video_title = Column(String(80), nullable=False)
    # video_type = Column(String(80), nullable=False)
    upload_date = Column(DateTime, nullable=False)
    filename_base = Column(String(200), nullable=False)
    duration = Column(Integer, nullable=False)
    collection_name = Column(String(200))

    # Not used on init
    ignore = Column(Boolean, nullable=False, default=False)
    plex_id = Column(String(40), default="")

    # Relationships
    # One to Many
    files = relationship("SourceFile", back_populates="source")
    tracks = relationship("Track", back_populates="source")

    # Many to One
    album_id = Column(Integer, ForeignKey("albums.id"))
    album = relationship("Album", back_populates="sources")

    def __repr__(self):
        return "SourceModel(id=%d,video_title=%s, url=%s,)" % (
            self.id,
            self.video_title,
            self.url,
        )


class Track(Base, CommonModel):
    __tablename__ = "tracks"
    # Required
    track_title = Column(String(200), nullable=False)
    start_time = Column(Integer, nullable=False, default=0)  # in ms
    end_time = Column(Integer, nullable=False, default=0)
    track_number = Column(Integer, nullable=False)

    # Not used on init
    # not sure where this is in the plexapi.
    # there should be a way to do it without matching files...
    plex_id = Column(String(40), default="")

    # Relationships
    # Track -> File (One to Many)
    files = relationship("TrackFile", back_populates="track")

    # (Many to One)
    album_id = Column(Integer, ForeignKey("albums.id"))
    album = relationship("Album", back_populates="tracks")
    source_id = Column(Integer, ForeignKey("sources.id"))
    source = relationship("Source", back_populates="tracks")

    # (Many to Many)
    artists = relationship("Artist", secondary="track_artists", back_populates="tracks")
    words = relationship("Word", secondary="track_words", back_populates="tracks")
    tags = relationship("Tag", secondary="track_tags", back_populates="tracks")
    producers = relationship(
        "Producer", secondary="track_producers", back_populates="tracks"
    )
    beats = relationship("Beat", secondary="track_beats", back_populates="tracks")

    def __repr__(self):
        return "TrackModel(id=%d,track_title=%s)" % (self.id, self.track_title)


class Album(Base, CommonModel):
    __tablename__ = "albums"
    # Init
    album_name = Column(String(200), nullable=False, unique=True)
    path = Column(String(200), nullable=False)
    track_prefix = Column(String(200), default="")
    sources = relationship("Source", back_populates="album")
    #     # Relationships
    #     # (One to Many)

    #     files = db.relationship("File", back_populates="album") # should have an image file
    tracks = relationship("Track", back_populates="album")
    files = relationship("AlbumFile", back_populates="album")

    def __repr__(self):
        return "Album(id=%d,album_name=%s)" % (self.id, self.album_name)


class Word(Base, CommonModel):
    __tablename__ = "words"

    # Required
    word = Column(String(200))
    tracks = relationship("Track", secondary="track_words", back_populates="words")

    def __repr__(self):
        return "Word(id=%d,word=%s)" % (self.id, self.word)


class Producer(Base, CommonModel):
    __tablename__ = "producers"
    # Required
    producer = Column(String(200), nullable=False)
    youtube_url = Column(String(200))
    tracks = relationship(
        "Track", secondary="track_producers", back_populates="producers"
    )

    def __repr__(self):
        return "Producer(id=%d,producer=%s)" % (self.id, self.producer)


class Beat(Base, CommonModel):
    __tablename__ = "beats"
    # Required
    beat_name = Column(String(200), nullable=False)

    # producer = Column(String(200), nullable=False)

    tracks = relationship("Track", secondary="track_beats", back_populates="beats")

    def __repr__(self):
        return "Beat(id=%d,beat_name=%s)" % (self.id, self.beat_name)


class Tag(Base, CommonModel):  # type: ignore
    __tablename__ = "tags"
    # Required
    # need to add sequence order
    tag = Column(String(200))
    tracks = relationship("Track", secondary="track_tags", back_populates="tags")

    def __repr__(self):
        return "Tag(id=%d,tag=%s)" % (self.id, self.tag)


class Artist(Base, CommonModel):  # type: ignore
    __tablename__ = "artists"
    # Required
    # need to add sequence order
    artist = Column(String(200))
    tracks = relationship("Track", secondary="track_artists", back_populates="artists")

    def __repr__(self):
        return "Artist(id=%d,artist=%s)" % (self.id, self.artist)


class TrackWord(Base):
    __tablename__ = "track_words"
    track_id = Column(ForeignKey("tracks.id"), primary_key=True)
    word_id = Column(ForeignKey("words.id"), primary_key=True)
    index = Column(Integer, nullable=False)


class TrackTag(Base):
    __tablename__ = "track_tags"
    track_id = Column(ForeignKey("tracks.id"), primary_key=True)
    tag_id = Column(ForeignKey("tags.id"), primary_key=True)
    sequence_order = Column(Integer, nullable=False)


class TrackProducer(Base):
    __tablename__ = "track_producers"
    track_id = Column(ForeignKey("tracks.id"), primary_key=True)
    producer_id = Column(ForeignKey("producers.id"), primary_key=True)
    sequence_order = Column(Integer, nullable=False)


class TrackBeat(Base):
    __tablename__ = "track_beats"
    track_id = Column(ForeignKey("tracks.id"), primary_key=True)
    beat_id = Column(ForeignKey("beats.id"), primary_key=True)
    sequence_order = Column(Integer, nullable=False)


class TrackArtist(Base):
    __tablename__ = "track_artists"
    track_id = Column(ForeignKey("tracks.id"), primary_key=True)
    artist_id = Column(ForeignKey("artists.id"), primary_key=True)
    sequence_order = Column(Integer, nullable=False)


class MediaFile(object):

    file_name = Column(String(200), nullable=False, unique=True)

    # this should probably be some type of enum structure
    file_type = Column(String(200), nullable=False)


class AlbumFile(Base, MediaFile, CommonModel):
    __tablename__ = "album_files"

    album_id = Column(Integer, ForeignKey("albums.id"))
    album = relationship("Album", back_populates="files")

    def __repr__(self):
        return "AlbumFile(id=%d,file_name=%s)" % (self.id, self.file_name)


class TrackFile(Base, MediaFile, CommonModel):
    __tablename__ = "track_files"
    # Init
    track_id = Column(Integer, ForeignKey("tracks.id"))
    track = relationship("Track", back_populates="files")

    def __repr__(self):
        return "TrackFile(id=%d,file_name=%s)" % (self.id, self.file_name)


class SourceFile(Base, MediaFile, CommonModel):
    __tablename__ = "source_files"
    # Init
    source_id = Column(Integer, ForeignKey("sources.id"))
    source = relationship("Source", back_populates="files")

    def __repr__(self):
        return "SourceFile(id=%d,file_name=%s)" % (self.id, self.file_name)
