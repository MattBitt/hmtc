from dataclasses import dataclass
from pathlib import Path

from hmtc.models import File as FileModel
from hmtc.models import FileType as FileTypeModel


@dataclass(frozen=True)
class FileTypesInterface:
    file_types_model: FileTypeModel
    object_type: str

    @staticmethod
    def from_filename(filename: Path) -> "FileTypesInterface":
        _ft = FileTypeModel.identify_file_type(filename)
        new_file = FileModel.create(filename=filename)
        return FileTypesInterface(file_model=new_file, object_type="file")


@dataclass(frozen=True)
class FileInterface:
    file_model: FileModel
    object_type: str

    @staticmethod
    def from_filename(filename: Path) -> "FileInterface":
        _ft = FileTypesInterface.from_filename(filename)
        new_file = FileModel.create(filename=filename)
        return FileInterface(file_model=new_file, object_type="file")
