from pathlib import Path

import ffmpeg

"""
commands taken from here:
https://www.reddit.com/r/ffmpeg/comments/hw57yb/extract_chapters_to_a_txt_file/

ffprobe -v quiet -print_format json -show_chapters input.mp4 > chapters.txt

ffmpeg -i input.mp4 -f ffmetadata output.txt


"""


def extract_video(input: Path, output: Path, start_time: int, end_time: int):
    try:
        _input = str(input)
        _output = str(output)
        input_file = ffmpeg.input(_input)

        input_file.output(_output, vcodec="copy", ss=start_time, to=end_time).run()
    except Exception as e:
        raise Exception(f"Error ripping track: {e}")


def extract_audio(input: Path, output: Path, start_time: int, end_time: int):
    # Load the video file
    try:
        _input = str(input)
        _output = str(output)
        input_file = ffmpeg.input(_input)

        # Extract the audio and save it as an MP3 file
        input_file.output(_output, acodec="mp3", ss=start_time, to=end_time).run()
    except Exception as e:
        raise Exception(f"Error ripping track: {e}")


if __name__ == "__main__":
    extract_video(
        "hmtc/utils/temp/6sYh6iuMUA8.webm",
        "hmtc/utils/temp/sample.mp4",
        "00:10:00",
        "00:12:34",
    )
