import re
from pathlib import Path

from loguru import logger

# this seems to work pretty well to convert vtt to lrc
# jellyfin seems to be able to read lrc files, but haven't
# seen a way to autoscroll anything


def create_lyrics_file(input_file: Path, output_file: Path, section):
    convert_vtt_to_lrc(
        input_file, output_file, time_range=(section.start / 1000, section.end / 1000)
    )


# need a max limit for time range (in seconds)
def convert_vtt_to_lrc(input_file: str, output_file: str, time_range=(0, 1000000)):
    file = Path(input_file)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
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
    with open(output_file, "w", encoding="utf-8") as f:
        for line in useful:
            new_line = line.replace("<c>", "").replace("</c>", "")
            modified_text = re.sub(
                r"^(.*?)<(\d{2}:\d{2}:\d{2}\.\d{3})>", r"[\2] \1", new_line, count=1
            )
            modified_text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", modified_text)
            timestamp = re.search(r"\[(\d{2}:\d{2}:\d{2}\.\d{3})\]", modified_text)
            if timestamp:
                orig_time_string = timestamp.group(1)
                # logger.debug(f"Time: {orig_time_string}")
                time_parts = orig_time_string.split(":")
                time_seconds = (
                    int(time_parts[0]) * 3600
                    + int(time_parts[1]) * 60
                    + float(time_parts[2])
                )
                if time_seconds < time_range[0] or time_seconds > time_range[1]:
                    continue
                else:
                    if time_range[0] > 0:
                        time_seconds = time_seconds - time_range[0]
                        hour = int(time_seconds / 3600)
                        minute = int((time_seconds % 3600) / 60)
                        second = int(time_seconds % 60)
                        milliseconds = int((second - int(second)) * 1000)
                        new_time_string = (
                            f"{hour:02}:{minute:02}:{second:02}.{milliseconds:03}"
                        )
                        modified_text = modified_text.replace(
                            f"[{orig_time_string}]", f"[{new_time_string}]"
                        )
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


if __name__ == "__main__":
    convert_vtt_to_lrc("hmtc/utils/example.vtt", "hmtc/utils/output.lrc")
