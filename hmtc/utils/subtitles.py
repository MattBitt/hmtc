import re

import ffmpeg
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


def remove_duplicated_captions(captions):
    """
    Removes or merges duplicate captions with identical or overlapping text in successive lines.

    Args:
        captions (list of dict): List of captions with 'start', 'end', and 'text'.

    Returns:
        list of dict: Cleaned captions with duplicates handled.
    """

    cleaned_captions = []

    for caption in captions:
        if cleaned_captions:
            last_caption = cleaned_captions[-1]

            # Check if the text is identical or the current text starts with the last text
            if caption["text"].startswith(last_caption["text"]):
                # Merge the times
                last_caption["end"] = caption["end"]
                # Update the text to include the new content
                last_caption["text"] = (
                    last_caption["text"]
                    + "\n"
                    + caption["text"][len(last_caption["text"]) :]
                )
                continue

        # Otherwise, add the current caption to the cleaned list
        cleaned_captions.append(caption)

    return cleaned_captions


# i generated the following with gpt on 1/27/25
def find_closest_caption(seconds, captions, n=2):
    """
    Finds the closest caption to the given timestamp and includes n lines around it.

    Args:
        seconds (int): The timestamp in seconds to find the closest caption for.
        captions (list of dict): A list of captions with 'start', 'end', and 'text' keys.
        n (int): The number of surrounding lines to include (default is 2).

    Returns:
        dict: A dictionary with the following keys:
            - 'captions': A list of captions (including the closest and surrounding lines).
            - 'highlight_index': The index of the closest caption in the returned list.
    """

    def timestamp_to_seconds(timestamp):
        """Converts a timestamp in HH:MM:SS format to total seconds."""
        pattern = r"align:start position:0%"
        _timestamp = re.sub(pattern, "", timestamp).strip()
        h, m = map(int, _timestamp.split(":")[:2])
        s, ms = map(float, _timestamp.split(":")[2].split("."))
        return h * 3600 + m * 60 + s + (ms / 1000)

    # Validate inputs
    if not captions or not isinstance(captions, list):
        return None

    # Convert timestamps to seconds and store in a new list for processing
    for caption in captions:
        caption["start_seconds"] = (
            timestamp_to_seconds(caption["start"]) if caption["start"] else None
        )
        caption["end_seconds"] = (
            timestamp_to_seconds(caption["end"]) if caption["end"] else None
        )

    # Find the closest caption
    closest_index = None
    min_diff = float("inf")
    for i, caption in enumerate(captions):
        if caption["start_seconds"] is not None and caption["end_seconds"] is not None:
            # Calculate the mid-point of the caption's interval
            mid_point = (caption["start_seconds"] + caption["end_seconds"]) / 2
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
            {"start": caption["start"], "end": caption["end"], "text": caption["text"]}
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
    # _captions = remove_duplicated_captions(captions)
    for caption in captions:
        text = caption["text"].lower()
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

    try:
        (
            ffmpeg.input(input_vtt)
            .output(output_srt, format="srt")
            .run(capture_stdout=False, capture_stderr=False)
        )
        logger.debug(f"Successfully converted {input_vtt} to {output_srt}")
        return output_srt
    except ffmpeg.Error as e:
        logger.error(f"Error converting subtitles: {e.stderr.decode()}")
        return None


if __name__ == "__main__":
    # Example usage
    convert_vtt_to_srt(
        "hmtc/utils/temp/omegle_50.en.vtt", "hmtc/utils/temp/omegle_50.srt"
    )
