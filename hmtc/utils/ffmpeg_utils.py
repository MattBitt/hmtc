import ffmpeg


"""
commands taken from here:
https://www.reddit.com/r/ffmpeg/comments/hw57yb/extract_chapters_to_a_txt_file/

ffprobe -v quiet -print_format json -show_chapters input.mp4 > chapters.txt

ffmpeg -i input.mp4 -f ffmetadata output.txt


"""


def extract_audio(input: str, output: str):
    ### command ffmpeg -i sample.avi -q:a 0 -map a sample.mp3

    # Load the video file
    input_file = ffmpeg.input(input)

    # Extract the audio and save it as an MP3 file
    input_file.output(output, acodec="mp3").run()


if __name__ == "__main__":
    extract_audio("hmtc/utils/sample.webm", "hmtc/utils/sample.mp3")
