import peewee
from pathlib import Path
from dataclasses import dataclass
from typing import List
from hmtc.models import (
    Bird as BirdModel,
    File as FileModel,
    FileType as FileTypeModel,
)
from hmtc.pages import db
from loguru import logger
from hmtc.config import init_config

config = init_config()


@dataclass(frozen=True)
class FileInterface:
    path: Path
    file_model: FileModel
    object_type: str

    @staticmethod
    def from_path(path: Path) -> "FileInterface":
        pass

    @staticmethod
    def from_id(bird_id: int) -> "FileInterface":
        pass


@dataclass(frozen=True)
class BirdFiles:
    bird_id: int
    image: FileInterface
    video: FileInterface
    audio: FileInterface

    @staticmethod
    def load(bird_id: int) -> "BirdFiles":
        pass

    def add_file(self, path: Path) -> FileInterface:
        pass

    def delete_file(self, path: Path) -> None:
        pass


@dataclass(frozen=True)
class BirdManager:
    bird_model: BirdModel
    bird_files: BirdFiles

    @staticmethod
    def create(
        species: str, weight: int, color: str, files: list = []
    ) -> "BirdManager":

        with db.atomic():
            try:
                _bird = BirdModel(species=species, weight=weight, color=color)
                for file in files:
                    _bird.add_file(file)
            except Exception as e:
                logger.error(f"Error creating bird: {e}")
                raise e

        _bird.save()
        bird_files = []
        return BirdManager(bird_model=_bird, bird_files=bird_files)

    @staticmethod
    def load(*args, **kwargs) -> "BirdManager":
        try:
            if "id" in kwargs:
                bird = BirdModel.get(BirdModel.id == kwargs["id"])
            elif "species" in kwargs:
                bird = BirdModel.get(BirdModel.species == kwargs["species"])
            else:
                raise ValueError("No valid arguments found")

        except Exception as e:
            logger.debug(f"Bird not found: {e, args, kwargs}")
            raise e
        bird_files = []
        return BirdManager(bird_model=bird, bird_files=bird_files)

    def delete_me(self) -> None:
        try:
            self.bird_model.delete_instance()
        except Exception as e:
            logger.error(f"Error deleting bird: {e}")
            db.rollback()
            raise e


if __name__ == "__main__":
    logger.debug(f"Initial: # birds = {BirdModel.select().count()}")

    with db.atomic():
        try:
            bird = BirdManager.create(species="robin", weight=15, color="red")
            logger.debug(f"Step #1 = {BirdModel.select().count()}")
        except peewee.IntegrityError as e:
            logger.error(f"Error creating bird: {e}")

        try:
            bird = BirdManager.create(species="blue jay", weight=20, color="blue")
            logger.debug(f"Step #3 = {BirdModel.select().count()}")
        except Exception as e:
            logger.error(f"Error creating bird: {e}")

        try:
            loaded_bird = BirdManager.load(species="robin")
            logger.debug(f"Step #4 = {loaded_bird.bird_model.species}")
        except Exception as e:
            logger.error(f"Error loading bird: {e}")

        try:
            new_bird = BirdManager.load(species="blue jay")
        except Exception as e:
            logger.error(f"Error loading bird: {e}")

        for file in new_bird.bird_files:
            logger.debug(f"File: {file}")
        else:
            logger.debug(f"No files found for bird")

        db.rollback()
    logger.debug(f"After Rollback: # birds = {BirdModel.select().count()}")
