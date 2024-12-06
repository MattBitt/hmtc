from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from hmtc.models import BaseModel
from hmtc.models import Bird as BirdModel
from hmtc.models import BirdFile as BirdFileModel
from hmtc.models import FileType as FileTypeModel


def _get_file_type(filename: Path) -> FileTypeModel:
    return "image"


@dataclass()
class BirdFileInterface:
    file_model: BirdFileModel
    bird_model: BirdModel

    @staticmethod
    def add_file(filename: Path) -> "BirdFileInterface":

        _ft = _get_file_type(filename)
        file_type, created = BirdFileModel(
            filename=filename, file_type=_ft
        ).get_or_create()

        new_file = BirdFileModel.create(filename=filename, file_type=file_type)
        return BirdFileInterface(file_model=new_file, object_type=f"{_ft}_file")
