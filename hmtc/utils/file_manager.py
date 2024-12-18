import shutil
from pathlib import Path

from loguru import logger


class FileManager:
    def __init__(self, model, filetypes, path):
        self.model = model
        self.filetypes = filetypes
        self.path = path

    def add_file(self, item, file: Path):
        # logger.debug(f"Adding file {file} to 'item' {item}")

        filetype = self.get_filetype(file.name)
        if filetype not in self.filetypes:
            raise ValueError(f"Invalid filetype {filetype}")
        if not "storage" in str(file):
            logger.debug(f"Moving file {file} to storage")
            try:
                _file = file.rename(self.path / file.name)
            except OSError as e:
                logger.error(f"Error moving file {file} to storage: {e}")
                if e.errno == 18:  # Invalid cross-device link
                    shutil.move(file, self.path / file.name)
                    _file = self.path / file.name
                else:
                    raise
        else:
            _file = file

        file_dict = dict(name=str(_file), size=_file.stat().st_size, filetype=filetype)

        self.model.create(**file_dict, item_id=item.id)
        # this is where i would create the file in the db
        # and actually put the file where it goes

    def get_filetype(self, file):
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

    def count_all(self):
        return self.model.select().count()

    def get_file(self, item_id, filetype):
        return (
            self.model.select()
            .where(self.model.item_id == item_id, self.model.filetype == filetype)
            .get()
        )
