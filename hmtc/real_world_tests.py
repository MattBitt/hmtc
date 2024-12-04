import peewee
from pathlib import Path
from dataclasses import dataclass
from typing import List
from hmtc.models import (
    Bird as BirdModel,
    BirdFile as BirdFileModel,
    FileType as FileTypeModel,
)
from hmtc.pages import db
from loguru import logger
from hmtc.config import init_config

config = init_config()


@dataclass(frozen=True)
class BirdFileInterface:
    path: Path
    bird_file: BirdFileModel

    @staticmethod
    def from_path(path: Path) -> "BirdFileInterface":
        bird_file = BirdFileModel.get(BirdFileModel.path == str(path))
        return BirdFileInterface(path=path, bird_file=bird_file)

    @staticmethod
    def from_id(bird_id: int) -> "BirdFileInterface":
        bird_file = BirdFileModel.get(BirdFileModel.id == bird_id)
        path = Path(bird_file.path)
        return BirdFileInterface(path=path, bird_file=bird_file)


@dataclass(frozen=True)
class BirdManager:
    bird: BirdModel
    bird_files: List[BirdFileInterface] = None

    @staticmethod
    def create(
        species: str, weight: int, color: str, files: list = []
    ) -> "BirdManager":

        with db.atomic():
            try:
                bird = BirdModel(species=species, weight=weight, color=color)
                for file in files:
                    bird.add_file(file)
            except Exception as e:
                logger.error(f"Error creating bird: {e}")
                raise e

        bird.save()
        return BirdManager(bird=bird)

    @staticmethod
    def load_from_db(*args, **kwargs) -> "BirdManager":
        try:
            if "id" in kwargs:
                bird = BirdModel.get(BirdModel.id == kwargs["id"])
            elif "species" in kwargs:
                bird = BirdModel.get(BirdModel.species == kwargs["species"])
            else:
                raise ValueError("No valid arguments found")

        except Exception as e:
            logger.debug(f"Bird not found: {e, args, kwargs}")
            raise ValueError(f"Bird not found: {e, args, kwargs}")
        return BirdManager(bird=bird)

    def add_file(self, filename: str) -> BirdFileInterface:
        _filename = Path(filename)
        return BirdFileInterface.from_path(path=_filename)

    def _add_file(self, filename: str) -> BirdFileModel:
        _ft = "poster"
        try:
            ft, created = FileTypeModel.get_or_create(title=_ft)
        except Exception as e:
            db.rollback()
            raise e
        bird_file = BirdFileModel.create(
            bird_id=self.bird.id,
            file_type=ft,
            path="somepath",
            filename=filename,
            verified_on_disk=None,
        )
        logger.debug(f"Added file {filename} to bird {self.bird.species}")
        return bird_file

    def delete_me(self):

        try:
            self.bird.delete_instance()
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
            bird.add_file("testing.jpg")
            logger.debug(f"Step #2 = {BirdModel.select().count()}")
        except Exception as e:
            logger.error(f"Error adding file: {e}")

        try:
            bird = BirdManager.create(species="blue jay", weight=20, color="blue")
            logger.debug(f"Step #3 = {BirdModel.select().count()}")
        except Exception as e:
            logger.error(f"Error creating bird: {e}")

        db.rollback()
    logger.debug(f"After Rollback: # birds = {BirdModel.select().count()}")
