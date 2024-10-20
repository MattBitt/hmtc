from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from hmtc.config import init_config
from hmtc.models import Track as TrackModel
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.section import Section
from hmtc.schemas.video import VideoItem
from hmtc.utils.ffmpeg_utils import rip_track

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


@dataclass
class TrackItem:
    # this defintely shouldn't be happening here.
    # track_folder = STORAGE / "tracks"
    # if not track_folder.exists():
    #     track_folder.mkdir()

    title: str = None
    track_number: int = 0
    length: int = 0
    album_id: int = None
    album_title: str = None

    def from_model(track: TrackModel) -> "TrackItem":
        return TrackItem(
            title=track.title,
            track_number=track.track_number,
            length=track.length,
            album_id=track.album_id,
        )

    # 🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    # 10/18/24 - the code below may or not be useful. I think i created it
    # to get some tracks built before our vacation to chicago. leaving it
    # in for now., but don't add anything here

    @staticmethod
    def create_from_section(video: VideoItem, album, section: Section) -> "TrackItem":
        logger.error(f"Creating track from section {section} for video {video}")
        title = video.title
        if title is None:
            logger.error(f"Video {video} has no title. Skipping")
            return None
        video_id = video.id
        track_number = AlbumItem.get_next_track_number(album)
        epno = None
        if album is not None:
            album_id = album.id
            if TrackItem.album_title is None:
                is_omegle, epno = is_omegle_bars(video.title)
                if is_omegle:
                    TrackItem.album_title = f"Omegle Bars {epno}"
                else:
                    TrackItem.album_title = album.title
        start_time = section.start
        end_time = section.end
        if epno is None:
            epno = 0
        t = TrackItem(
            title=f"{epno}.{track_number}",
            track_number=track_number,
            video_id=video_id,
            album_id=album_id,
            start_time=start_time,
            end_time=end_time,
        )
        t.save_to_db()
        return t

    def save_to_db(self):
        logger.error(f"Saving track {self}")
        track = TrackModel(
            title=self.title,
            track_number=self.track_number,
            length=self.length,
            album_id=self.album_id,
        )
        track.save()

    def write_file(self):
        source = VideoItem.get_audio_file_path(self.video_id)
        if source is None:
            logger.error(f"Could not find audio file for video {self.video_id}")
            return
        out_folder = self.track_folder / f"{TrackItem.album_title}/"
        if not out_folder.exists():
            out_folder.mkdir(parents=True)
        dest = str(out_folder / f"{self.track_number} - {self.title}.mp3")
        logger.error(f"Ripping track from {source} to {dest}")
        # rip_track(source, dest, start_time=self.start_time, end_time=self.end_time)
