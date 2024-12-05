from dataclasses import dataclass
from pathlib import Path
from hmtc.models import BaseModel
from hmtc.models import Bird as BirdModel
from hmtc.models import BirdFile as BirdFileModel
from hmtc.models import File as FileModel
from hmtc.models import FileType as FileTypeModel
from loguru import logger


def _get_file_type(filename: Path) -> FileTypeModel:
    return "image"


@dataclass()
class FileInterface:
    my_path: str
    file_model: FileModel


class BirdFileInterface(FileInterface):
    file_model: BirdFileModel
    bird_model: BirdModel

    @staticmethod
    def add_file(filename: Path) -> "FileInterface":
        _ft = _get_file_type(filename)
        file_type, created = BirdFileModel(file_type=_ft).get_or_create()
        if created:
            logger.debug(f"Created new file type: {file_type}")
        new_file = FileModel.create(filename=filename, file_type=file_type)
        return FileInterface(file_model=new_file, object_type=f"{_ft}_file")
