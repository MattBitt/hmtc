from pathlib import Path

from loguru import logger


class FileManager:
    def __init__(self, model, filetypes):
        self.model = model
        self.filetypes = filetypes

    def add_file(self, item, file: Path):
        logger.debug(f"Adding file {file} to 'item' {item}")
        file_dict = dict()
        filetype = self.get_filetype(file.name)
        if filetype not in self.filetypes:
            raise ValueError(f"Invalid filetype {filetype}")
        file_dict["name"] = file.name
        file_dict["size"] = file.stat().st_size
        file_dict["filetype"] = filetype
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
