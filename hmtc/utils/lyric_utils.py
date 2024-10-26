from loguru import logger
from pathlib import Path
import re

# this seems to work pretty well to convert vtt to lrc
# jellyfin seems to be able to read lrc files, but haven't
# seen a way to autoscroll anything


def read_vtt(filename):
    file = Path(filename)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    useful = []
    brackets = []
    times = []
    other = []
    empty = []
    with open(file, "r") as f:
        lines = f.readlines()
        line1 = lines[0].strip()  # WEBVTT
        line2 = lines[1].strip()  # Kind: captions
        line3 = lines[2].strip()  # Language: en
        for line in lines[3:]:

            l = line.strip()
            if l == "":
                empty.append(l)
                continue
            if l.startswith("["):
                brackets.append(l)
            elif "-->" in l:
                times.append(l)
            else:
                if "<c>" not in l:
                    other.append(l)
                else:
                    useful.append(l)
    with open("output.lrc", "w", encoding="utf-8") as f:
        for line in useful:
            new_line = line.replace("<c>", "").replace("</c>", "")
            modified_text = re.sub(
                r"^(.*?)<(\d{2}:\d{2}:\d{2}\.\d{3})>", r"[\2] \1", new_line, count=1
            )
            modified_text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", modified_text)
            f.write(modified_text + "\n")
    logger.debug(f"Brackets: {len(brackets)}")
    logger.debug(f"Times: {len(times)}")
    logger.debug(f"Other: {len(other)}")
    logger.debug(f"Empty: {len(empty)}")
    logger.debug(f"Total lines: {len(lines)}")
    logger.debug(
        f"Total Identified: {len(brackets) + len(times) + len(other) + len(empty)}"
    )
    logger.debug(f"Useful: {len(useful)}")


read_vtt("hmtc/utils/example.vtt")
