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


# Example usage
captions = [
    {"start": "00:00:01.000", "end": "00:00:03.000", "text": "Caption 1"},
    {
        "start": "00:00:03.001",
        "end": "00:00:06.000",
        "text": "Caption 1\nwith more text",
    },
    {"start": "00:00:07.000", "end": "00:00:09.000", "text": "Caption 2"},
    {"start": "00:00:10.000", "end": "00:00:12.000", "text": "Caption 3"},
    {"start": "00:00:13.000", "end": "00:00:15.000", "text": "Caption 3\ncontinued"},
]

result = remove_duplicated_captions(captions)
print(result)  # For testing purposes
