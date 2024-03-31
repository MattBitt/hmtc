from topic import Topic

import cv2


class FrameAnalyzer:
    def __init__(self, frame, current_clip):
        # frame is an image grabbed from the livestream to analyze
        # current_clip is the currently active clip on the livestream
        # will eventually be at least topic and instrumentals (any others?)
        self.frame = frame
        self.current_clip = current_clip

    def found_same_topic(self, previous_topic):
        if previous_topic is None:
            return False
        new_topic = Topic(self.frame, previous_topic.contour)
        if previous_topic == new_topic:
            return True
        else:
            return False

    def analyze_frame(self):
        topic_contour = self.find_topic_contour()
        if topic_contour is not None:
            topic = Topic(self.frame, topic_contour)
            return topic
        else:
            return None

    def find_topic_contour(self):
        # this is testing a new algorithim
        cropped = self.frame[0:720, 0:640]  # crop out right half of image
        blurred = cv2.GaussianBlur(cropped, (5, 5), 1)
        b, g, r = cv2.split(blurred)

        ret, blue_thresh = cv2.threshold(b, 127, 255, cv2.THRESH_BINARY)
        ret, green_thresh = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY)
        ret, red_thresh = cv2.threshold(r, 127, 255, cv2.THRESH_BINARY)
        # probably doesn't need to be a dict.  just trying using it identify
        # superchat colors
        thresholds = [
            {"name": "blue", "thresh": blue_thresh},
            {"name": "green", "thresh": green_thresh},
            {"name": "red", "thresh": red_thresh},
        ]
        possible_contours = []
        for thresh in thresholds:
            # temp_image = cropped.copy()
            contours, hierarchy = cv2.findContours(
                image=thresh["thresh"],
                mode=cv2.RETR_EXTERNAL,
                method=cv2.CHAIN_APPROX_NONE,
            )
            # need a good number for min area
            filtered = filter(
                lambda contour_area: cv2.contourArea(contour_area) >= 40000, contours
            )
            # why do i have to do this?
            f_list = list(filtered)
            # if len(f_list) == 1:
            #     possible_contours.append(f_list[0])
            #     continue
            for contour in f_list:
                x, y, w, h = cv2.boundingRect(contour)
                if h > w:
                    # need a rectangle thats wider than tall
                    # this may not always be true.  earlier vids superchats were
                    # closer to square
                    continue
                if x > 200:
                    # need a rectangle on the left side of the screen
                    continue
                else:
                    possible_contours.append(contour)

        if len(possible_contours) == 0:
            return None
        elif len(possible_contours) == 1:
            return possible_contours[0]
        else:
            highest_contour_y = 5000
            for pc in possible_contours:
                _, y, _, _ = cv2.boundingRect(pc)
                if y < highest_contour_y:
                    highest_contour_y = y
                    correct_contour = pc

        return correct_contour


def is_same_contours(con1, con2):
    # check if 2 contours are basically the same shape and
    # position
    margin = 10  # px

    x1, y1, w1, h1 = cv2.boundingRect(con1)
    x2, y2, w2, h2 = cv2.boundingRect(con2)
    if (
        abs(x1 - x2) > margin
        or abs(y1 - y2) > margin
        or abs(w1 - w2) > margin
        or abs(h1 - h2) > margin
    ):
        return False
    else:
        return True


# class ScreenGrab:
#     def __init__(self, image):
#         self.image = image.copy()
#         # self.topic = self.parse_image_for_topic()
#         # self.instrumental = self.parse_image_for_instrumental()

#     # def parse_image_for_topic(self):
#     #     topic_contour = self.find_topic_contour()
#     #     if topic_contour is None:
#     #         # no topic found
#     #         return None

#     #     image = crop_to_contour(self.image, topic_contour)
#     #     return Topic(image)

#     def parse_image_for_instrumental(self, active_instrumental):
#         return None

#     def find_topic_contour(self):
#         # this is testing a new algorithim
#         cropped = self.image[0:720, 0:640]  # crop out right half of image
#         blurred = cv2.GaussianBlur(cropped, (5, 5), 1)
#         b, g, r = cv2.split(blurred)

#         ret, blue_thresh = cv2.threshold(b, 127, 255, cv2.THRESH_BINARY)
#         ret, green_thresh = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY)
#         ret, red_thresh = cv2.threshold(r, 127, 255, cv2.THRESH_BINARY)
#         thresholds = [blue_thresh, green_thresh, red_thresh]
#         possible_contours = []
#         for thresh in thresholds:
#             # temp_image = cropped.copy()
#             contours, hierarchy = cv2.findContours(
#                 image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE
#             )
#             # need a good number for min area
#             filtered = filter(
#                 lambda contour_area: cv2.contourArea(contour_area) >= 40000, contours
#             )
#             # why do i have to do this?
#             f_list = list(filtered)
#             # if len(f_list) == 1:
#             #     possible_contours.append(f_list[0])
#             #     continue
#             for contour in f_list:
#                 x, y, w, h = cv2.boundingRect(contour)
#                 if h > w:
#                     # need a rectangle thats wider than tall
#                     # this may not always be true.  earlier vids superchats were
#                     # closer to square
#                     continue
#                 if x > 200:
#                     # need a rectangle on the left side of the screen
#                     continue
#                 else:
#                     possible_contours.append(contour)

#         if len(possible_contours) == 0:
#             return None
#         elif len(possible_contours) == 1:
#             return possible_contours[0]
#         else:
#             highest_contour_y = 5000
#             for pc in possible_contours:
#                 _, y, _, _ = cv2.boundingRect(pc)
#                 if y < highest_contour_y:
#                     highest_contour_y = y
#                     correct_contour = pc
#         return correct_contour
