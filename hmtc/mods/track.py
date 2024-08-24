from dataclasses import dataclass
from loguru import logger
from hmtc.models import Track as TrackTable
from hmtc.schemas.video import VideoItem
from hmtc.mods.section import Section
from hmtc.mods.album import Album as AlbumItem
from hmtc.config import init_config
from hmtc.utils.ffmpeg_utils import rip_track
from pathlib import Path

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


def is_omegle_bars(title: str):
    if title is None:
        return False, None
    if "omegle bars" in title.lower():
        try:
            epno = int(title.split(" ")[-1])
            return True, epno
        except ValueError:
            return False, None
    return False, None


@dataclass
class TrackItem:
    track_folder = STORAGE / "tracks"
    if not track_folder.exists():
        track_folder.mkdir()

    title: str
    track_number: str
    video_id: int
    album_id: int
    start_time: int
    end_time: int
    album_title: str = None

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
        track = TrackTable(
            title=self.title,
            track_number=self.track_number,
            video_id=self.video_id,
            album_id=self.album_id,
            start_time=self.start_time,
            end_time=self.end_time,
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
        rip_track(source, dest, start_time=self.start_time, end_time=self.end_time)
