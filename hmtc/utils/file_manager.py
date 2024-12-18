from loguru import logger


class FileManager:
    def __init__(self, model):
        self.model = model

    def add_file(self, item, file):
        logger.debug(f"Adding file {file} to 'item' {item}")
        self.model.create(**file, item_id=item.id)
        # this is where i would create the file in the db
        # and actually put the file where it goes
