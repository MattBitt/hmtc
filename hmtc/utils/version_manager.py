from loguru import logger

VERSION_FILE = "hmtc/.version"


def get_version():
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()


def increment_version():
    with open(VERSION_FILE, "r") as f:
        version = int(f.read().strip())
    with open(VERSION_FILE, "w") as f:
        f.write(str(version + 1))


if __name__ == "__main__":
    increment_version()
    logger.info(f"Version updated to {get_version()}")
