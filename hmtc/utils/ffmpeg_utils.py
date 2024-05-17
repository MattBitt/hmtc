"""
commands taken from here:
https://www.reddit.com/r/ffmpeg/comments/hw57yb/extract_chapters_to_a_txt_file/

ffprobe -v quiet -print_format json -show_chapters input.mp4 > chapters.txt

ffmpeg -i input.mp4 -f ffmetadata output.txt


"""
