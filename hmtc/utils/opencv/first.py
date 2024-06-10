from datetime import datetime, timedelta

import cv2


class VideoToImagesWithTimestamps:
    def __init__(self, video_path, output_folder, start_time, time_interval=1):
        self.video_path = video_path
        self.output_folder = output_folder
        self.start_time = start_time
        self.time_interval = timedelta(seconds=time_interval)
        self.frame_count = 0

        # Open the video
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise Exception("Error: Could not open the video.")

    def split_video_to_images_with_timestamps(self):
        while True:
            ret, frame = self.cap.read()

            if not ret:
                break

            image_filename = f"{self.output_folder}/frame_{self.frame_count:04d}.jpg"
            self._add_timestamp_to_frame(frame)
            cv2.imwrite(image_filename, frame)

            self.frame_count += 1

    def _add_timestamp_to_frame(self, frame):
        timestamp = self.start_time + self.frame_count * self.time_interval
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            frame, timestamp_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )

    def release_video(self):
        self.cap.release()


if __name__ == "__main__":
    video_path = "static/video.webm"
    output_folder = "output_images"
    start_time = datetime(2023, 9, 1, 10, 0, 0)
    time_interval = 10000  # Optional, set the time interval in seconds

    video_to_images = VideoToImagesWithTimestamps(
        video_path, output_folder, start_time, time_interval
    )

    try:
        video_to_images.split_video_to_images_with_timestamps()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        video_to_images.release_video()
