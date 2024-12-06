from dataclasses import dataclass, asdict

from loguru import logger

from hmtc.config import init_config

config = init_config()


@dataclass(frozen=True, kw_only=True)
class BaseDomain:
    base_data: str = "No data supplied"

    def some_method(self):
        return self.base_data
