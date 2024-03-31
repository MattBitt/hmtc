from frame_analyzer import FrameAnalyzer
from clip import Clip
from collections import deque
import cv2
from pathlib import Path
import csv
from collections import Counter

# from progress.bar import Bar
from tqdm import tqdm


class LiveStreamVideo:
    def __init__(self, video):
        # for now, use folder to get frames

        self.video = video
        self.current_clip = None
        self.debounce_queue = deque([], maxlen=5)
        self.topic_clips = []

    def open_video(self):
        self.video = cv2.VideoCapture(str(self.video_file))
        self.get_video_fps()

    def get_video_fps(self):
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split(".")
        if int(major_ver) < 3:
            self.fps = self.video.get(cv2.cv.CV_CAP_PROP_FPS)
        else:
            self.fps = self.video.get(cv2.CAP_PROP_FPS)

    def close_video(self):
        cv2.destroyAllWindows()
        self.video.release()

    def process_video(self):

        # leave this as screen grabs for now
        # once testing is finished should change to video file
        # instead
        MODE = "screengrabs"

        if MODE == "screengrabs":
            frame_source = self.get_frame_from_images
            frame_counter = self.count_frames_in_folder
        else:
            frame_source = self.get_frames
            frame_counter = self.count_frames

        total_frames = frame_counter()
        frame_counter = 0

        # with Bar("Processing...", max=total_frames) as bar:
        for frame in tqdm(
            frame_source(),
            total=total_frames,
            desc="Processing Video...",
            mininterval=0.5,
        ):
            frame_counter += 1
            if self.current_clip is None:
                self.current_clip = Clip(0, frame, topic=None)
                for i in range(5):
                    self.debounce_queue.append(self.current_clip.topic)
            fa = FrameAnalyzer(frame, self.current_clip)
            if fa.found_same_topic(self.current_clip.topic):
                self.debounce_queue.append(self.current_clip.topic)
                continue

            topic = fa.analyze_frame()
            self.debounce_queue.append(topic)

            # not sure when this would occur
            if self.current_clip.topic == topic:
                continue

            if self.debounce_queue.count(topic) == 5:
                if self.current_clip.topic != topic:
                    clip_number = len(self.topic_clips) + 1
                    self.current_clip.finish(clip_number, frame_counter - 5)
                    # dont need to do this for now
                    # if self.current_clip.topic is not None:
                    #     self.current_clip.topic.find_superchat_color()
                    self.topic_clips.append(self.current_clip)
                    self.current_clip = Clip(frame_counter - 5, frame, topic)

        clip_number = len(self.topic_clips) + 1
        self.current_clip.finish(clip_number, frame_counter)
        self.topic_clips.append(self.current_clip)
        return self.topic_clips

    def get_frames(self):
        pass

    def count_frames(self):
        pass

    def count_frames_in_folder(self):
        return len(list(self.video.glob("*.png")))

    def get_frame_from_images(self):
        # this is only for debugging purposes
        self.current_frame_count = 0
        files = self.video.glob("WW*.png")

        if files:
            for f in files:
                # uncomment next lines to quickly limit how much video
                # should be processed, only for testing
                # if self.current_frame_count >= 200:
                #     break
                self.current_frame_count += 1
                image = cv2.imread(str(f))
                yield image
        else:
            return None

        # self.close_video()


def extract_topic_images_from_video(source_folder, target_folder, videos):
    # vid = LiveStreamVideo(folder / (video_file + ".mp4"))
    for vid in videos:
        print(f"Processing video: {vid}")
        lsv = LiveStreamVideo(source_folder / vid)
        topic_clips = lsv.process_video()

        for tc in topic_clips:
            if tc.topic is not None:
                cv2.imwrite(
                    str(
                        target_folder / vid / (vid + "_" + str(tc.clip_number) + ".png")
                    ),
                    tc.topic.image,
                )


def extract_clips_from_video(source_folder, target_folder, videos):
    for vid in videos:
        print(f"Processing video: {vid}")
        lsv = LiveStreamVideo(source_folder / vid)
        topic_clips = lsv.process_video()
        clips = []
        for tc in tqdm(
            topic_clips,
            desc="Processing Text From Clips...",
            mininterval=0.5,
        ):
            text_to_add = [
                vid,
                tc.clip_number,
                tc.start_time,
                tc.end_time,
            ]
            if tc.topic is not None:
                t = tc.topic
                t.find_superchat_color()
                t.read_text_from_image()
                text_to_add.extend([t.color, t.user, t.donation, t.text, t.words])
            else:
                text_to_add.extend(["", "", "", "", ""])
            clips.append(text_to_add)
            # if tc.topic is not None:

            #     cv2.imwrite(
            #         str(
            #             target_folder / vid / (vid + "_" + str(tc.clip_number) + ".png")
            #         ),
            #         tc.topic.image,
            #     )

        fields = (
            "filename",
            "clip_number",
            "start_time",
            "end_time",
            "color",
            "user",
            "donation",
            "text",
            "words",
        )
        fname = target_folder / (vid + ".csv")
        with open(fname, "w") as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)

            # writing the fields
            csvwriter.writerow(fields)

            # writing the data rows
            csvwriter.writerows(clips)


def find_letter_counts(target_folder, csv_file):
    # opening the CSV file
    users = []
    donations = []
    text = []
    with open(str(target_folder / csv_file), mode="r") as file:

        # reading the CSV file
        csvFile = csv.reader(file)

        # displaying the contents of the CSV file
        for lines in csvFile:
            if lines[4] != "color" and lines[5] != "user":
                chars = lines[5].lower().strip()
                if chars:
                    users.extend(list(chars))
        # letters = []
        # counter = Counter(colors_found)
    letter_counts = Counter(users)
    print(letter_counts)
    # all_chars = sorted([i if letter_counts[i] > 0 else None for i in letter_counts])
    # bad_chars = [i for i in all_chars if not i.isalnum()]
    # print("".join(bad_chars))
    fields = ("letter", "occurrances")

    output_file = str(target_folder / (csv_file + "_letters.csv"))
    with open(output_file, "w") as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields
        csvwriter.writerow(fields)

        # writing the data rows
        csvwriter.writerows(clips)


def find_key_words(target_folder, csv_file):
    with open(str(target_folder / csv_file), mode="r") as file:

        # reading the CSV file
        csvFile = csv.reader(file)

        # displaying the contents of the CSV file
        words = []
        for lines in csvFile:
            if lines[4] != "color" and lines[5] != "user":
                text = (lines[8].lower().strip()).split(" ")
                words.extend(text)
        word_counts = list(Counter(list(words)).items())

        fields = ("words", "occurrances")
        output_file = str(target_folder / (csv_file + "_words.csv"))
        with open(output_file, "w") as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)

            # writing the fields
            csvwriter.writerow(fields)

            # writing the data rows
            csvwriter.writerows(word_counts)


if __name__ == "__main__":
    # source_folder = Path('/sources/video/Harry Mack/Wordplay Wednesday/')
    source_folder = Path("temp_images/screengrabs/")
    target_folder = Path("test_images/output/topics_from_video/")
    videos = [
        "WW091",
        "WW094",
        "WW095",
        "WW096",
        "WW097",
        # "WW080",
        # "WW091",
    ]

    for vid in videos:
        if not (source_folder / vid).exists():
            raise IOError
        if not (target_folder / vid).exists():
            (target_folder / vid).mkdir(parents=True)
    extract_clips_from_video(source_folder, target_folder, videos)
    # find_letter_counts(target_folder, videos[0] + ".csv")
    for vid in videos:
        find_key_words(target_folder, vid + ".csv")

    # extract_topic_images_from_video(source_folder, target_folder, videos)

    #        )
# class oldLiveStreamVideo:
#     def __init__(self, video_file):
#         self.MIN_FRAMES_ACTIVE = (
#             5  # needs to be on screen for this many frames (or seconds?)
#         )
#         self.video_file = video_file

#         if not self.video_file.exists():
#             raise IOError

#         self.current_frame_count = 0
#         self.current_topic = None
#         self.current_topic_contour = None
#         self.current_instrumental = None
#         self.topic_clips = []
#         self.potential_new_topic = []
#         self.instrumental_clips = []
#         self.potential_new_instrumental = []

#         # self.start_new_topic_clip()
#         # self.start_new_instrumental_clip()

#     def get_frame(self):
#         # initialize counter
#         self.current_frame_count = 0

#         while self.video.isOpened():
#             # only here for testing purposes
#             # probably should create some short videos for testing
#             # this should only run for the first time
#             if self.current_frame_count >= 200:
#                 break
#             success, current_frame = self.video.read()
#             if success:
#                 self.current_frame_count += 1
#                 if not (
#                     self.current_frame_count % self.fps
#                 ):  # sample one frame each second
#                     yield current_frame
#         print(f"Done processing {str(self.current_frame_count )} videos")

#     def process_video(self):
#         self.open_video()
#         self.topic_clips.append(Clip(0, 0, None))
#         for frame in self.get_frame_from_images():
#             current_frame = ScreenGrab(frame)
#             if self.current_topic_contour is not None:
#                 a = crop_to_contour(current_frame, self.current_topic_contour)
#                 if self.current_topic.image == a:
#                     # checking the same roi as the current topic.  looks like it matches
#                     # so move on to the next frame
#                     continue
#             new_topic = current_frame.parse_image_for_topic()
#             # various scenarios possible here
#             # found a topic (but has to be different then the current)
#             #
#             if self.should_start_new_topic_clip(new_topic):
#                 self.start_new_topic_clip(new_topic)
#             # if self.should_start_new_instrumental_clip():
#             #     self.start_new_instrumental_clip()

#         return self.topic_clips, self.instrumental_clips

#     def should_start_new_topic_clip(self, new_topic):
#         # if different than active but first time found in a row
#         if (
#             len(self.potential_new_topic) == 0
#             or new_topic != self.potential_new_topic[-1]
#         ):
#             self.potential_new_topic = [new_topic]
#             return False

#         # this topic has already been found but not promoted to active yet
#         self.potential_new_topic.append(new_topic)
#         if len(self.potential_new_topic) == self.MIN_FRAMES_ACTIVE:
#             return True

#     def start_new_topic_clip(self, new_topic):
#         if len(self.topic_clips) > 0:  # no old topics to close out
#             self.topic_clips[-1].finish(self.current_frame_count - 1)
#         topic_clip = Clip(self.current_frame_count, len(self.topic_clips), new_topic)
#         self.topic_clips.append(topic_clip)

#     def should_start_new_instrumental_clip(self):
#         if len(self.instrumental_clips) == 0:
#             return True
#         else:
#             return False

#     def start_new_instrumental_clip(self):
#         if len(self.instrumental_clips) > 0:  # no old instrumentals to close out
#             self.instrumental_clips[-1].finish(self.current_frame_count - 1)
#         instrumental_clip = Clip(
#             self.current_frame_count,
#             len(self.instrumental_clips),
#             self.current_frame.instrumental,
#         )
#         self.instrumental_clips.append(instrumental_clip)
