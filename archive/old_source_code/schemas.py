from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime


class SourceBaseSchema(BaseModel):
    url: str
    video_title: str
    # video_type: str
    ignore: Optional[bool] = False
    plex_id: Optional[str] = ""
    upload_date: date
    duration: Optional[int]
    filename_base: str
    collection_name: Optional[str] = ""
    created: Optional[datetime]
    modified: Optional[datetime]
    # when a source is created, it shouldn't have an album reference yet
    # after establishing the source, the album name/details should be created
    album_id: Optional[int]

    class Config:
        orm_mode = True

    @validator("upload_date", pre=True)
    def date_validate(cls, v):
        if type(v) == str:
            return datetime.strptime(v, "%m-%d-%Y")
        else:
            return v

    # this is how I did the relationship with Marshmallow
    # tracks = List(fields.Nested(TrackSchema(exclude=("id", "source"))))


class SourceSchema(SourceBaseSchema):
    id: int

    class Config:
        orm_mode = True


class TrackBaseSchema(BaseModel):
    track_title: str
    source_id: int
    start_time: Optional[int] = 0
    end_time: Optional[int] = 0
    track_number: str
    plex_id: Optional[str] = ""
    album_id: Optional[int]

    class Config:
        orm_mode = True

    # this is how I did the relationship with Marshmallow
    # source = fields.Nested(lambda: SourceSchema(only=("id", "video_title")))


class TrackSchema(TrackBaseSchema):
    id: int

    class Config:
        orm_mode = True


class AlbumBaseSchema(BaseModel):
    album_name: str
    path: str
    track_prefix: Optional[str] = ""

    class Config:
        orm_mode = True

    # this is how I did the relationship with Marshmallow
    # source = fields.Nested(lambda: SourceSchema(only=("id", "video_title")))


class AlbumSchema(AlbumBaseSchema):
    id: int

    class Config:
        orm_mode = True


class WordBaseSchema(BaseModel):
    word: str

    class Config:
        orm_mode = True


class WordSchema(WordBaseSchema):
    id: int

    class Config:
        orm_mode = True


class ProducerBaseSchema(BaseModel):
    producer: str
    youtube_url: Optional[str]

    class Config:
        orm_mode = True


class ProducerSchema(ProducerBaseSchema):
    id: int

    class Config:
        orm_mode = True


class TagBaseSchema(BaseModel):
    tag: str

    class Config:
        orm_mode = True


class TagSchema(TagBaseSchema):
    id: int

    class Config:
        orm_mode = True


class BeatBaseSchema(BaseModel):
    beat_name: str

    class Config:
        orm_mode = True


class BeatSchema(BeatBaseSchema):
    id: int

    class Config:
        orm_mode = True


class MediaFileSchema(BaseModel):
    file_name: str
    file_type: str


class AlbumFileSchema(MediaFileSchema):
    album_id: int

    class Config:
        orm_mode = True


class SourceFileSchema(MediaFileSchema):
    source_id: int

    class Config:
        orm_mode = True


class TrackFileSchema(MediaFileSchema):
    track_id: int

    class Config:
        orm_mode = True


class ArtistBaseSchema(BaseModel):
    artist: str

    class Config:
        orm_mode = True


class ArtistSchema(ArtistBaseSchema):
    id: int

    class Config:
        orm_mode = True


class AlbumWithRelationships(AlbumSchema):
    sources: List[SourceSchema]
    tracks: List[TrackSchema]
    files: List[AlbumFileSchema]


class SourceWithRelationships(SourceSchema):
    album: AlbumWithRelationships
    tracks: List[TrackSchema]
    files: List[SourceFileSchema]


class WordWithRelationships(WordSchema):
    tracks: List[TrackSchema]


class TrackWithRelationships(TrackSchema):
    source: SourceSchema
    album: AlbumSchema
    words: List[WordSchema]
    tags: List[TagSchema]
    producers: List[ProducerSchema]
    beats: List[BeatSchema]
    artists: List[ArtistSchema]
    files: List[TrackFileSchema]


class TagWithRelationships(TagSchema):
    tracks: List[TrackSchema]


class ProducerWithRelationships(ProducerSchema):
    tracks: List[TrackSchema]


class BeatWithRelationships(BeatSchema):
    tracks: List[TrackSchema]


class ArtistWithRelationships(ArtistSchema):
    tracks: List[TrackSchema]


class WhatsPlayingSchema(BaseModel):
    media_type: str
    current_time: int
    media_info: SourceWithRelationships | TrackSchema
