import re

import webvtt
from loguru import logger


def parse_vtt_remove_duplicates(file_path):
    """
    Parses a YouTube-generated VTT file, combines duplicate and overlapping lines, and
    returns a list of unique captions with consolidated start and end times.

    Args:
        file_path (str): Path to the .vtt file to parse.

    Returns:
        list of dict: A list of unique captions with keys: 'start', 'end', 'text'.
    """
    captions = []

    def normalize_text(text):
        """Removes timestamps and excessive whitespace from text."""

        return re.sub(r"<.*?>", "", text).strip()

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    start, end, text = None, None, ""
    for line in lines:
        line = line.strip()

        if "-->" in line:  # Timestamp line
            if text.strip():  # Save the previous caption
                normalized_text = normalize_text(text)
                if captions and captions[-1]["text"] in normalized_text:
                    # Extend the previous caption's end time
                    captions[-1]["end"] = end
                    captions[-1]["text"] = (
                        captions[-1]["text"]
                        + " "
                        + normalized_text[len(captions[-1]["text"]) :]
                    )
                else:
                    # Add a new unique caption
                    captions.append(
                        {"start": start, "end": end, "text": normalized_text}
                    )
            start, end = line.split(" --> ")
            text = ""  # Reset text for the new caption
        elif line:  # Text line
            text += " " + line

    # Add the last caption if necessary
    if text.strip():
        normalized_text = normalize_text(text)
        if captions and captions[-1]["text"] in normalized_text:
            captions[-1]["end"] = end
            captions[-1]["text"] = (
                captions[-1]["text"]
                + " "
                + normalized_text[len(captions[-1]["text"]) :]
            )
        else:
            captions.append({"start": start, "end": end, "text": normalized_text})

    return captions


def find_caption_by_time(seconds, captions):
    """
    Finds the caption whose interval encompasses the given time in seconds.

    Args:
        seconds (int): The time in seconds to search for.
        captions (list of dict): A list of captions with 'start', 'end', and 'text' keys.

    Returns:
        dict or None: The caption dict that encompasses the time, or None if not found.
    """

    def timestamp_to_seconds(timestamp):
        """Converts a timestamp in HH:MM:SS format to total seconds."""
        pattern = r"align:start position:0%"
        _timestamp = re.sub(pattern, "", timestamp).strip()
        h, m = map(
            int, _timestamp.split(":")[:2]
        )  # Extract hours and minutes as integers
        s, ms = map(
            float, _timestamp.split(":")[2].split(".")
        )  # Split seconds and milliseconds
        return h * 3600 + m * 60 + s + (ms / 1000)

    for caption in captions:
        if caption["start"] is None or caption["end"] is None:
            continue
        start_seconds = timestamp_to_seconds(caption["start"])
        end_seconds = timestamp_to_seconds(caption["end"])
        if start_seconds <= seconds <= end_seconds:
            return caption
    return None


def read_vtt(vtt_file):
    _captions = parse_vtt_remove_duplicates(vtt_file)
    return _captions


def analyze_subtitle_density(vtt_file):
    vtt = webvtt.read(vtt_file)

    # Initialize variables
    subtitle_density = []
    last_end_time = 0
    talking_segments = []
    music_segments = []

    # Analyze each caption
    for caption in vtt:
        start_time = caption.start_in_seconds
        end_time = caption.end_in_seconds
        text = caption.text.strip()

        # Calculate the duration of the caption
        duration = end_time - start_time

        # If there is a gap between the last caption and the current one, record it
        if last_end_time < start_time:
            gap_duration = start_time - last_end_time
            subtitle_density.append(
                (last_end_time, start_time, 0)
            )  # No subtitles in this gap

            # Check if the gap is significant (e.g., more than 1 second)
            if gap_duration > 1:
                music_segments.append(
                    (last_end_time, start_time)
                )  # Potential music segment

        # Record the current caption's density
        subtitle_density.append(
            (start_time, end_time, len(text.split()))
        )  # Count words as density
        last_end_time = end_time
        talking_segments.append((start_time, end_time, text))  # Record talking segment

    # Check for any remaining gap after the last caption
    if last_end_time < vtt[-1].end_in_seconds:
        gap_duration = vtt[-1].end_in_seconds - last_end_time
        if gap_duration > 1:
            music_segments.append(
                (last_end_time, vtt[-1].end_in_seconds)
            )  # Potential music segment

    return {
        "subtitle_density": subtitle_density,
        "talking_segments": talking_segments,
        "music_segments": music_segments,
    }


if __name__ == "__main__":
    # Example usage
    result = analyze_subtitle_density("hmtc/utils/temp/omegle_50.en.vtt")
    # print("Subtitle Density:", result["subtitle_density"])
    # print("Talking Segments:", result["talking_segments"])
    print("Music Segments:", result["music_segments"])
