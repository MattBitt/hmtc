from dataclasses import dataclass
from hmtc.config import init_config


config = init_config()


@dataclass
class DatabaseItem:
    name: str
    description: str

    @staticmethod
    def run_procedure(prodedure_name: str):
        pass

    @staticmethod
    def get_downloaded_percent_by_series():
        sql = ""
