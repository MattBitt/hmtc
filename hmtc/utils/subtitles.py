import re
from datetime import datetime, timedelta
from pathlib import Path

import ffmpeg
import srt
from loguru import logger
from thefuzz import fuzz


# i generated the following with gpt on 1/27/25
def find_closest_caption(seconds, captions, n=3):
    """
    Finds the closest caption to the given timestamp and includes n lines around it.

    Args:
        seconds (int): The timestamp in seconds to find the closest caption for.
        captions (list of Subtitle Objects ):
        n (int): The number of surrounding lines to include (default is 2).

    Returns:
        dict: A dictionary with the following keys:
            - 'captions': A list of captions (including the closest and surrounding lines).
            - 'highlight_index': The index of the closest caption in the returned list.
    """

    # Validate inputs
    if not captions or not isinstance(captions, list):
        return None

    # Find the closest caption
    closest_index = None
    min_diff = float("inf")
    for i, caption in enumerate(captions):

        # Calculate the mid-point of the caption's interval
        mid_point = ((caption.start + caption.end) / 2).total_seconds()
        diff = abs(seconds - mid_point)
        if diff < min_diff:
            min_diff = diff
            closest_index = i

    if closest_index is None:
        return None

    # Extract n lines around the closest caption
    start_index = max(0, closest_index - n)
    end_index = min(len(captions), closest_index + n + 1)
    surrounding_captions = captions[start_index:end_index]

    # Calculate highlight index
    highlight_index = closest_index - start_index

    # Prepare the output dictionary
    result = {
        "captions": [
            {"start": caption.start, "end": caption.end, "text": caption.content}
            for caption in surrounding_captions
        ],
        "highlight_index": highlight_index,
    }

    return result


def find_substantial_phrase_lines(captions, phrases, threshold=0.4):
    """
    Finds timestamps or indices of captions where the text consists mostly (e.g., 80%) of specific phrases.

    Args:
        captions (list of dict): List of captions with 'start', 'end', and 'text'.
        phrases (list of str): List of phrases to search for.
        threshold (float): The minimum proportion of text that must match phrases (default is 0.8).

    Returns:
        list of dict: A list of dictionaries containing 'start', 'end', and 'text' for captions meeting the criteria.
    """
    matching_captions = []

    for caption in captions:
        text = caption.content.strip().lower()
        # Split text into words and count total words
        words = re.findall(r"\w+", text)
        total_words = len(words)
        if total_words == 0:
            continue

        # Count how many words match the phrases
        match_count = sum(
            1
            for word in words
            if any(
                re.fullmatch(rf"{re.escape(phrase.lower())}", word)
                for phrase in phrases
            )
        )

        # Check if the match proportion meets or exceeds the threshold
        if match_count / total_words >= threshold:
            matching_captions.append(caption)

    return matching_captions


def convert_vtt_to_srt(input_vtt, output_srt):
    """Converts a VTT subtitle file to SRT format using ffmpeg."""

    #    try:
    if not input_vtt.exists():
        logger.error(f"Input File DOES NOT EXIST")
        return
    elif output_srt.exists():
        logger.error(f"OUTPUT File ALREADY EXISTS")
        return

    try:
        input = ffmpeg.input(str(input_vtt))
        input.output(str(output_srt), format="srt", loglevel="verbose").run()
    except Exception as e:
        logger.error(f"FFMPEG ERROR: {e} {e.stderr.decode()}")
    input_vtt.unlink()
    return output_srt


def read_srt_file(file):
    with open(file, "r") as f:
        raw_subs = r"{}".format(f.read())
    if raw_subs is None:
        logger.error(f"Error Parsing subtitle file {file}")
        return None
    data = srt.parse(raw_subs)

    return list(data)


# created with gpt on 1/28/25 after choosing srt instead of vtt


def merge_subtitles(subtitle_path):
    """Merge subtitles while keeping the most unique text and minimizing entries using srt library."""
    subtitles = read_srt_file(subtitle_path)
    merged_subs = []

    for sub in subtitles:
        # the shortest duration captions are the single 'phrases'
        # they always come together with the 2 line version
        # checking for short ones avoids parsing the longer ones
        dur = (sub.end - sub.start).total_seconds()
        if dur < 1:
            merged_subs.append(sub)

    return merged_subs


def rip_subs_from_srt(input: Path, output: Path, time_range: tuple = None):
    """Extracts a portion of subtitles from an SRT file based on the specified time range."""
    if time_range is None or len(time_range) != 2:
        logger.error("Invalid time range provided.")
        return

    start_time, end_time = time_range
    subtitles = read_srt_file(input)
    extracted_subs = []

    for sub in subtitles:
        if (
            sub.start.total_seconds() >= start_time
            and sub.end.total_seconds() <= end_time
        ):
            extracted_subs.append(sub)

    with open(output, "w") as f:
        f.write(srt.compose(extracted_subs))

    logger.info(f"Extracted {len(extracted_subs)} subtitles to {output}.")


def extract_subs(input: Path, output: Path, start_time: int, end_time: int):

    try:
        rip_subs_from_srt(input, output, (start_time, end_time))

    except Exception as e:
        raise Exception(f"Error ripping track: {e}")


if __name__ == "__main__":
    # Example usage
    subtitles = "hmtc/utils/temp/omegle_50.srt"
    result = merge_subtitles(subtitles)
    print(len(result))
