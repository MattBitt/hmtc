class Clip:
    def __init__(self, start_time, original_image, topic=None):
        self.start_time = start_time
        self.clip_number = None
        self.original_image = original_image
        self.topic = topic

    def finish(self, clip_number, timestamp):
        self.clip_number = clip_number
        self.end_time = timestamp

    def __repr__(self):
        has_topic = self.topic is not None
        return f"Clip {str(self.clip_number)} --> {self.start_time}:{self.end_time} --> has_topic: {has_topic}"

    def __str__(self):
        has_topic = self.topic is not None
        return f"Clip {str(self.clip_number)} --> {self.start_time}:{self.end_time} --> has_topic: {has_topic}"
