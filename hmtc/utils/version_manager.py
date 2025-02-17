from loguru import logger

VERSION_FILE = "hmtc/.version"


def get_version():
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()


def increment_version():
    version = ""
    with open(VERSION_FILE, "r") as f:
        version = f.read().strip()

    a, b, c = version.split(".")
    new_version = f"{a}.{b}.{int(c) + 1}"
    with open(VERSION_FILE, "w") as f:
        f.write(str(new_version))


if __name__ == "__main__":
    increment_version()
    logger.info(f"Version updated to {get_version()}")
