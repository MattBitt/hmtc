import shutil
from pathlib import Path

from loguru import logger

from hmtc.domains.base_domain import BaseDomain


class FileManager:
    def __init__(self, model, filetypes, path: Path):
        self.model = model
        self.filetypes = filetypes
        if not path.exists():
            raise FileNotFoundError(f"Path {path} not found")
        self.path = path

    def add_file(self, item: BaseDomain, file: Path, to_move=False):

        if not file.exists():
            raise FileNotFoundError(f"File {file} not found")

        filetype = self.get_filetype(file.name)

        if to_move:
            logger.debug(f"Moving file {file} to storage")
            try:
                final_file = file.rename(self.path / file.name)
            except OSError as e:
                logger.debug(f"Error moving file {file} to storage: {e}")
                if e.errno == 18:  # Invalid cross-device link
                    shutil.move(file, self.path / file.name)
                    final_file = self.path / file.name
                else:
                    raise Exception(f"Error moving file {file} to storage: {e}")
        else:
            final_file = file

        file_dict = dict(
            name=str(final_file),
            size=final_file.stat().st_size / 1000,  # in kB
            filetype=filetype,
        )

        self.model.create(**file_dict, item_id=item.instance.id)

    def delete_files(self, item_id):
        files = list(self.model.select().where(self.model.item_id == item_id))
        for file in files:
            Path(file.name).unlink()
            file.delete_instance()

    def get_filetype(self, file: Path):
        file_string = str(file)
        videos = [".mkv", ".mp4", ".webm"]
        audios = [".mp3", ".wav"]
        lyrics = [".lrc"]
        subtitles = [".srt", ".en.vtt"]
        infos = [".nfo", ".info.json", ".json", ".txt"]
        posters = [".jpg", ".jpeg", ".png", ".webp"]

        if file_string.endswith(tuple(videos)):
            return "video"

        if file_string.endswith(tuple(audios)):
            return "audio"

        if file_string.endswith(tuple(infos)):
            return "info"

        if file_string.endswith(tuple(lyrics)):
            return "lyrics"

        if file_string.endswith(tuple(subtitles)):
            return "subtitles"

        if file_string.endswith(tuple(posters)):
            return "poster"

        raise ValueError(f"Invalid filetype for {file_string}")

    def count(self):
        return self.model.select().count()

    def get_file(self, item_id, filetype):
        return (
            self.model.select()
            .where(self.model.item_id == item_id, self.model.filetype == filetype)
            .get()
        )

    def files(self, item_id):
        return self.model.select().where(self.model.item_id == item_id)

    def poster(self, item_id) -> Path:
        return self.get_file(item_id, "poster")
