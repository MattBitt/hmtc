from pathlib import Path
from typing import List, Optional, Union
from enum import Enum
from hmtc.models import BaseModel

class FileTypeNotSupportedError(Exception):
    pass

class FileRepo:
    # Map filetypes to their respective table/model classes
    FILETYPE_MAP = {
        "poster": "ImageTable",
        "audio": "AudioTable",
        "video": "VideoTable"
    }

    def __init__(self, model: BaseModel, item_id: int = 0):
        self.model = model
        self.item_id = item_id
        self.files = self.load_files() if item_id != 0 else []

    def get(self, filetype: Optional[str] = None) -> Union[List[BaseModel], BaseModel]:
        """
        Retrieve files, optionally filtered by filetype.
        Lazy loads files if not already loaded.
        """
        if not self.files:
            self.files = self.load_files()

        if filetype:
            # Filter files by type using getattr to dynamically access properties
            return next((f for f in self.files if getattr(f, f"{filetype}_id", None)), None)

        return self.files

    def load_files(self) -> List[BaseModel]:
        """Load all files associated with the item_id"""
        return list(self.model.select().where(self.model.item_id == self.item_id))

    # def poster(self) -> 'MyImage':
    #     """Get poster image file"""
    #     return MyImage(self.get("poster"))

    def mp3(self) -> Path:
        """Get audio file path"""
        return Path(self.get("audio"))

    def mkv(self) -> Path:
        """Get video file path"""
        return Path(self.get("video"))

    def add(self, file: Path) -> None:
        """
        Add a new file to the repository
        Args:
            file: Path to the file
            existing: Strategy for handling existing files ('overwrite' or 'append')
        """
        filetype = self._get_filetype(file)
        FileTable = self._convert_filetype_to_filetable(filetype)

        if not FileTable:
            raise FileTypeNotSupportedError(f"Filetype '{filetype}' is not supported")

        file_data = self._prepare_file_data(file)


        # Create new file entry
        FileTable.create(**file_data, item_id=self.item_id)
        
        # Refresh files list
        self.files = self.load_files()

