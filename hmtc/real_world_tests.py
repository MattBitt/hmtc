from dataclasses import dataclass
from pathlib import Path
from typing import List

import peewee
from loguru import logger

from hmtc.config import init_config
from hmtc.models import (
    Bird as BirdModel,
)
from hmtc.pages import db
from hmtc.schemas.file_interface import BirdFileInterface

config = init_config()


@dataclass(frozen=True)
class BirdFiles:
    bird_id: int
    image: BirdFileInterface
    video: BirdFileInterface
    audio: BirdFileInterface

    @staticmethod
    def load(bird_id: int) -> "BirdFiles":
        pass

    def add_file(self, path: Path) -> BirdFileInterface:
        pass

    def delete_file(self, path: Path) -> None:
        pass


@dataclass(frozen=True)
class BirdManager:
    bird_model: BirdModel
    bird_files: BirdFiles
    files_optional: bool = True

    @staticmethod
    def create(species: str, weight: int, color: str, files: list) -> "BirdManager":
        if not BirdManager.files_optional and not files:
            raise ValueError("Files are required for creating a bird")

        bird_files = []
        with db.atomic():
            try:
                _bird = BirdModel(species=species, weight=weight, color=color)
                for file in files:
                    logger.debug(f"Need to Adding file: {file} during creating bird")
                    new_bird_file = BirdFileInterface.add_file(file)
                    bird_files.append(new_bird_file)
            except Exception as e:
                logger.error(f"Error creating bird: {e}")
                raise e

        _bird.save()

        return BirdManager(bird_model=_bird, bird_files=bird_files)

    @staticmethod
    def load(*args, **kwargs) -> "BirdManager":
        try:
            if "id" in kwargs:
                _bird = BirdModel.get(BirdModel.id == kwargs["id"])
            elif "species" in kwargs:
                _bird = BirdModel.get(BirdModel.species == kwargs["species"])
            else:
                raise ValueError("No valid arguments found")

        except Exception as e:
            logger.debug(f"Bird not found: {e, args, kwargs}")
            raise e
        bird_files = []
        return BirdManager(bird_model=_bird, bird_files=bird_files)

    @staticmethod
    def how_many() -> int:
        return BirdModel.select().count()

    def delete_me(self) -> None:
        try:
            self.bird_model.delete_instance()
        except Exception as e:
            logger.error(f"Error deleting bird: {e}")
            db.rollback()
            raise e

    logger.debug(f"Initial: # birds = {BirdModel.select().count()}")


def bird_manager():
    with db.atomic():
        try:
            bird = BirdManager.create(species="robin", weight=15, color="red", files=[])
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


if __name__ == "__main__":
    bird_manager()
