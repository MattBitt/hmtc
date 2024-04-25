from hmtc.config import init_config
from hmtc.utils.my_logging import setup_logging
from hmtc.db import (
    create_tables,
)


def setup():
    config = init_config()
    setup_logging(config)
    db = create_tables()
    return db, config
