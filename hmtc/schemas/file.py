from dataclasses import dataclass
from pathlib import Path


from hmtc.schemas.base import BaseItem


@dataclass(frozen=True, kw_only=True)
class FileItem(BaseItem):
    path: str = None
    filename: str = None
    file_type: str = None
    video_id: int = None
    channel_id: int = None
    series_id: int = None
    playlist_id: int = None
    exists: bool = False

    @staticmethod
    def from_string(path: str, filename: str, file_type: str):
        return FileItem(path=path, filename=filename, file_type=file_type, exists=False)

    @staticmethod
    def from_path(path: Path, file_type=None):
        return FileItem(
            path=str(path), filename=path.name, file_type=None, exists=False
        )
