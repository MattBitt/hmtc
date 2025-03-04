from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from loguru import logger
from peewee import DoesNotExist, Model
from PIL import Image

T = TypeVar("T", bound="BaseDomain")


class BaseDomain:
    model: Model = None
    repo = None
    file_repo = None

    def __init__(self, item_id: Optional[int] = None):
        if item_id and self.repo is not None:
            self.instance = self.repo.get_by_id(item_id)
        else:
            self.instance = None

    @classmethod
    def create(cls: Type[T], data: Dict[str, Any]) -> T:
        instance = cls.model.create(**data)
        return cls(instance)

    def save(self) -> None:
        if self.instance:
            self.instance.save()

    def delete(self) -> None:
        if self.file_repo is not None:
            self.file_repo.delete_files(self.instance.id)

        if self.instance:
            self.instance.delete_instance()

    def update(self, data: Dict[str, Any]) -> "BaseDomain":
        for key, value in data.items():
            setattr(self.instance, key, value)
        self.instance.save()
        return self

    def serialize(self) -> Dict[str, Any]:
        return self.instance.my_dict()

    @classmethod
    def load(cls: Type[T], instance_id: int) -> Optional[T]:
        try:
            instance = cls.model.get(cls.model.id == instance_id)
            return cls(instance)
        except DoesNotExist:
            return None

    @classmethod
    def get_by(cls: Type[T], **kwargs: Any) -> Optional[T]:
        try:
            instance = cls.model.get(**kwargs)
            return cls(instance)
        except DoesNotExist:
            return None

    @classmethod
    def select_where(cls: Type[T], **kwargs: Any) -> List[T]:
        query = cls.model.query_from_kwargs(**kwargs)
        return [cls(instance) for instance in query]

    @classmethod
    def count(cls) -> int:
        return cls.model.select().count()

    # the methods for the domains that include files
    def add_file(self, file: Path):
        raise ValueError(f"asdfasdfasdf")

    def get_file(self, filetype) -> Path | None:
        _file = self.file_repo.get(item_id=self.instance.id, filetype=filetype)
        return Path(_file.path) if _file else None

    def poster(self, thumbnail=False):
        _poster = self.file_repo.get(self.instance.id, "poster")
        if _poster is None:
            return "Placeholder Image"
        if thumbnail:
            return Image.open(_poster.thumbnail.get().path)
        else:
            return Image.open(_poster.path)

    def poster_file(self):
        return self.file_repo.get(self.instance.id, "poster")

    def subtitles(self):
        _subtitles = self.file_repo.get(self.instance.id, "subtitle")
        if _subtitles is None:
            return None
        else:
            return Path(_subtitles.path)

    def video_file(self):
        video_file = self.file_repo.get(self.instance.id, "video")
        if video_file is None:
            return None
        else:
            return Path(video_file.path)

    def section_status_color(self):
        if self.num_sections() == 0:
            return "warning"
        if self.num_sections() > self.num_sections(fine_tuned=True):
            return "info"
        elif self.num_sections(fine_tuned=True) > self.num_tracks():
            return "warning"
        elif self.num_sections(
            fine_tuned=True
        ) > self.num_sections() or self.num_tracks() > self.num_sections(
            fine_tuned=True
        ):
            return "error"
        else:
            return "success"
        