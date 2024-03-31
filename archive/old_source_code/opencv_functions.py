import time
from typing import Optional, Tuple
import cv2
import pytesseract
from PIL import Image
import imagehash
import numpy as np
from glob import glob
from matplotlib import pyplot as plt
from sklearn import cluster
from pathlib import Path
from difflib import SequenceMatcher
import csv
import timeit


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def extract_images_from_video():
    START_VIDEO_NUMBER = 68
    INPUT_BASE_PATH = "/sources/video/Harry Mack/Wordplay Wednesday/Wordplay Wednesday "
    OUTPUT_BASE_PATH = "temp_images/screengrabs/WW"
    for num in range(20):
        # do 20 episodes at a time
        ep_number = str(START_VIDEO_NUMBER + num).zfill(3)
        out_folder = Path(OUTPUT_BASE_PATH + ep_number)
        if out_folder.exists():
            # if its already there, then skip it
            print(f"Skipping WW{ep_number}")
            continue
        out_folder.mkdir()
        video_path = INPUT_BASE_PATH + ep_number + ".mp4"
        print(video_path)

        cap = cv2.VideoCapture(video_path)
        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split(".")

        if int(major_ver) < 3:
            fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
            print(
                "Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(
                    fps
                )
            )
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(
                "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)
            )
        count = 0
        if not fps:
            exit()
        while cap.isOpened():
            success, image = cap.read()
            if success:

                count += 1
                if not (count % fps):  # sample one frame each second
                    file_number_str = str(int(count / fps)).zfill(6)
                    new_filename = (
                        f"{str(out_folder)}/WW{ep_number}_{file_number_str}.png"
                    )
                    cv2.imwrite(new_filename, image)
            else:
                break
        print(f"Counted {count} frames total")
        cv2.destroyAllWindows()
        cap.release()


def read_text_from_image(image, super_chat_color, text_color="black"):

    # Need to redo this whole section!!!!
    """Reads text from an image file and outputs found text to text file"""
    # Convert the image to grayscale
    save_image(image, "finding_text.png", hsv=False)
    scale_percent = 220
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    save_image(resized, "resized.png", hsv=False)
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    save_image(gray_image, "gray_image.png", hsv=False)
    # Perform Threshold
    if text_color == "white":  # always use white background/black text
        thresh = cv2.bitwise_not(gray_image)
        save_image(thresh, "inverting_white_text.png", hsv=False)
    else:
        thresh = gray_image

    if super_chat_color == "ORANGE":
        # no idea where these arguments came from...
        thresh = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 11
        )
    else:
        ret, thresh = cv2.threshold(
            thresh, 120, 255, cv2.THRESH_BINARY  # cv2.THRESH_OTSU
        )  # | cv2.THRESH_BINARY)

    save_image(thresh, "after_threshold.png", hsv=False)
    # rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    # kernel = np.ones((2, 2), np.uint8)
    # dilation = cv2.dilate(thresh, kernel, iterations=1)
    contours, hierachy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    image_copy = resized.copy()
    # draw_contours(image_copy, contours, "allcontours.png")

    text = ""
    print(f"contours found = {len(contours)}")
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        cropped = image_copy[y : y + h, x : x + w]
        # draw_contours(cropped, contour, "textcontour.png")
        text += pytesseract.image_to_string(cropped)
    print(text)
    return text


def create_color_mask(image, color):

    return cv2.inRange(image, color[0], color[1])


def save_image(im, filename, hsv=True):
    if im is None:
        return
    folder = "temp_images/output/"
    if hsv:
        cv2.imwrite(folder + filename, cv2.cvtColor(im, cv2.COLOR_HSV2BGR))
    else:
        cv2.imwrite(folder + filename, im)


def draw_contours(image, contours, filename):

    return cv2.drawContours(
        image=image,
        contours=contours,
        contourIdx=-1,
        color=(0, 255, 0),
        thickness=3,
        lineType=cv2.LINE_AA,
    )


def compute_mean_color(color1, color2):
    h1, s1, v1 = color1
    h2, s2, v2 = color2
    return ((h2 + h1) / 2, (s2 + s1) / 2, (v2 + v1) / 2)


def HSVtoOpenCVColors(color):
    h, s, v = color
    h = int(h / 2)
    s = int((s / 100) * 255)
    v = int((v / 100) * 255)
    return (h, s, v)


def calculate_thresholds(color, offset):
    h, s, v = color
    lower = np.array(
        [
            (h - offset) if h > offset else 0,
            (s - 2 * offset) if s > 2 * offset else 0,
            (v - offset) if 2 * v > 2 * offset else 0,
        ]
    )
    upper = np.array(
        [
            (h + offset) if (h + offset) < 180 else 180,
            (s + 2 * offset) if (s + 2 * offset) < 255 else 255,
            (v + 2 * offset) if (v + 2 * offset) < 255 else 255,
        ]
    )

    return (lower, upper)


def get_file_list(directory):
    files = glob(directory + "*.png")
    if files:
        return sorted(files)
    else:
        return None


def find_message_in_image(filename, current_time):
    # superchats have a color component as well
    img = cv2.imread(filename)
    # this function should examine the image and return the 'active' superchat
    # in the image

    message = find_superchat_in_image2(img, filename, current_time)

    return message


def crop_image_to_rect(filename, bouding_rect):
    image = cv2.imread(filename)
    img = image.copy()
    x, y, w, h = bouding_rect
    return img[y : y + h, x : x + w]


def find_superchat_in_image2(img, filename, current_time):
    # this is testing a new algorithim
    cropped = img[0:720, 0:640]  # crop out right half of image
    blurred = cv2.GaussianBlur(cropped, (5, 5), 1)
    b, g, r = cv2.split(blurred)

    ret, blue_thresh = cv2.threshold(b, 127, 255, cv2.THRESH_BINARY)
    ret, green_thresh = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY)
    ret, red_thresh = cv2.threshold(r, 127, 255, cv2.THRESH_BINARY)
    thresholds = [blue_thresh, green_thresh, red_thresh]
    possible_contours = []
    for thresh in thresholds:
        # temp_image = cropped.copy()
        contours, hierarchy = cv2.findContours(
            image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE
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
        # no possible superchats found
        super_chat = MessageClip(
            start_time=current_time,
            filename=filename,
        )
        return super_chat
    elif len(possible_contours) == 1:
        # only 1 possibility found.  no need for more checking
        # temp_contours = draw_contours(
        #     cropped.copy(), possible_contours[0], "filename not needed"
        # )
        x, y, w, h = cv2.boundingRect(possible_contours[0])
        image_copy = cropped[y : y + h, x : x + w]

        super_chat = MessageClip(
            start_time=current_time,
            filename=filename,
            image=image_copy,
            bounding_rect=cv2.boundingRect(possible_contours[0]),
        )

        return super_chat
    else:
        # now that i have found all of the contours, should sort by y coordinate
        # this doesn't currently do anything
        # how do i sort based on y coordinate?
        highest_contour_y = 5000
        for pc in possible_contours:
            _, y, _, _ = cv2.boundingRect(pc)
            if y < highest_contour_y:
                highest_contour_y = y
                correct_contour = pc
        # highest_contour = sorted(
        #     possible_contours, key=lambda x: cv2.contourArea(x), reverse=True
        # )

        # temp_contours = draw_contours(
        #     cropped.copy(), highest_contour[0], "filename not needed"
        # )
        x, y, w, h = cv2.boundingRect(correct_contour)
        image_copy = cropped[y : y + h, x : x + w]

        super_chat = MessageClip(
            start_time=current_time,
            filename=filename,
            image=image_copy,
            bounding_rect=(x, y, w, h),
        )

        return super_chat


def find_superchat_in_image(img, filename, current_time):
    # loop through the contours and decide if it is a message or not.
    # should be able to get chat, but probably don't need to
    # also think about grabbing the producer from images that have them too
    cropped = img[0:720, 0:640]  # crop out right half of image
    # save_image(cropped, "Step 1 - cropped.png", hsv=False)
    # img_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    # save_image(blur, "Step 3A - blurred.png", hsv=False)

    # ret, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # save_image(thresh, "Step 4A - thresh.png", hsv=False)

    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

    colors = [
        {"name": "pink", "header": (329, 100, 67), "body": (332, 100, 81)},
        {"name": "blue", "header": (183, 74, 81), "body": (180, 72, 97)},
        {"name": "green1", "header": (172, 99, 77), "body": (166, 87, 91)},
        {"name": "green2", "header": (165, 50, 73), "body": (155, 48, 89)},
        {"name": "orange1", "header": (20, 84, 82), "body": (20, 81, 89)},
        {"name": "orange2", "header": (23, 95, 91), "body": (28, 95, 96)},
        {"name": "yellow1", "header": (39, 73, 94), "body": (44, 68, 95)},
        {"name": "yellow2", "header": (44, 95, 99), "body": (46, 83, 99)},
        {"name": "red", "header": (10, 85, 72), "body": (10, 80, 80)},
    ]
    messages = []  # keep track of all messages found in the image

    for color in colors:
        # color_mask = cv2.inRange(hsv, (120, 200, 170), (190, 255, 255))
        # for this step, i want to create a mask for an average between
        # header and body.  need to be able to create masks for the header
        # and body separately as well
        blur = cv2.GaussianBlur(hsv, (7, 7), 0)
        # save_image(blur, "Step 4A - blurred (inrange).png", hsv=False)

        # mean_color = compute_mean_color(color["header"], color["body"])
        # opencv_color = HSVtoOpenCVColors(mean_color)
        # color_thresholds = calculate_thresholds(opencv_color, offset=25)
        # color_mask = create_color_mask(blur, color_thresholds)

        heading_color, body_color = (color["header"], color["body"])

        opencv_color = HSVtoOpenCVColors(heading_color)
        color_thresholds = calculate_thresholds(opencv_color, offset=35)
        heading_color_mask = create_color_mask(blur, color_thresholds)
        # save_image(
        #     heading_color_mask,
        #     f"Step 4B - in range color ({color['name']}).png",
        #     hsv=False,
        # )
        opencv_color = HSVtoOpenCVColors(body_color)
        color_thresholds = calculate_thresholds(opencv_color, offset=25)
        body_color_mask = create_color_mask(blur, color_thresholds)

        # save_image(
        #     body_color_mask,
        #     f"Step 4C - in range color ({color['name']}).png",
        #     hsv=False,
        # )
        color_mask = cv2.bitwise_or(heading_color_mask, body_color_mask)

        # Remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        opening = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, hierarchy = cv2.findContours(
            image=opening, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE
        )
        if not len(contours):
            pass
            # print(f"No contours found for {color['name']} ")

        # sorts all found contours by descending area.  only draw them for debugging purposes
        message_contours = sorted(
            contours, key=lambda x: cv2.contourArea(x), reverse=True
        )
        found_eligible = 0
        for contour in message_contours:
            x, y, w, h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 40000 and x < 150:
                messages.append(contour)
                found_eligible += 1
                # print(f"Found {found_eligible} {color['name']} eligible contours")
                # print(f"Countour paramters: x: {x} y: {y} w: {w} h: {h}")
        if not found_eligible:
            pass
            # print(f"Found NO {color['name']} eligible contours")

    high_y = 5000  # big number to be beaten
    final_message = None
    for message in messages:
        x, y, w, h = cv2.boundingRect(message)
        if y < high_y:
            final_message = message
            high_y = y
    # draw_contours(img, final_message, "allcontours.png")
    x, y, w, h = cv2.boundingRect(final_message)
    image_copy = cropped[y : y + h, x : x + w]
    # at this point, i have a superchat
    # when do I know that there is no superchat for this image
    # must be after i've checked every color.
    super_chat = MessageClip(
        start_time=current_time,
        filename=filename,
        image=image_copy,
        bounding_rect=(x, y, w, h),
    )

    return super_chat


def plot_histogram(filename):

    img = cv2.imread(filename)
    assert img is not None, "file could not be read, check with os.path.exists()"
    # plt.hist(img.ravel(), 256, [0, 256])
    color = ("b", "g", "r")
    for i, col in enumerate(color):
        histr = cv2.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(histr, color=col)
        plt.xlim([0, 256])
    plt.savefig("temp_images/output/final_histogram.png")
    plt.clf()
    plt.show()


def plot_hsv_histogram(img):
    # read image into range 0 to 1
    img = img / 255

    # set number of colors
    number = 4

    # quantize to 16 colors using kmeans
    h, w, c = img.shape
    img2 = img.reshape(h * w, c)
    kmeans_cluster = cluster.KMeans(n_clusters=number)
    kmeans_cluster.fit(img2)
    cluster_centers = kmeans_cluster.cluster_centers_
    cluster_labels = kmeans_cluster.labels_

    # need to scale back to range 0-255 and reshape
    img3 = cluster_centers[cluster_labels].reshape(h, w, c) * 255.0
    img3 = img3.astype("uint8")

    # cv2.imshow("reduced colors", img3)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # reshape img to 1 column of 3 colors
    # -1 means figure out how big it needs to be for that dimension
    img4 = img3.reshape(-1, 3)

    # get the unique colors
    colors, counts = np.unique(img4, return_counts=True, axis=0)
    print(colors)
    print("xxx")
    print(counts)
    unique = zip(colors, counts)

    # function to convert from r,g,b to hex
    def encode_hex(color):
        b = color[0]
        g = color[1]
        r = color[2]
        hex = "#" + str(bytearray([r, g, b]).hex())
        print(hex)
        return hex

    # plot each color
    fig = plt.figure()
    for i, uni in enumerate(unique):
        color = uni[0]
        count = uni[1]
        plt.bar(i, count, color=encode_hex(color))

    # show and save plot
    plt.savefig("temp_images/output/hsv_histogram.png")
    plt.close(fig)


def remove_avatar(im):
    # not sure if this is needed
    return im


def add_image_to_background(bg, image):
    # this will add image centered on bg and return the whole thing

    row, col = image.shape[:2]

    y_border_size = int((bg.shape[0] - row) / 2)
    x_border_size = int((bg.shape[1] - col) / 2)
    border = cv2.copyMakeBorder(
        image,
        top=y_border_size,
        bottom=y_border_size,
        left=x_border_size,
        right=x_border_size,
        borderType=cv2.BORDER_CONSTANT,
        value=[0, 0, 0],
    )

    # bg_h, bg_w = bg.shape
    # im_h, im_w, _ = image.shape
    # if im_w > bg_w or im_h > bg_h:
    #     print(f"image does not fit on background {str(image.shape)}")
    #     return None
    # x, y = (int(bg_w / 2 - im_w / 2), int(bg_h / 2 - im_h / 2))
    # bg[y : y + image.shape[0], x : x + image.shape[1]] = image[:2]

    return border


def add_text_to_image(
    image_rgb: np.ndarray,
    label: str,
    top_left_xy: Tuple = (10, 300),
    font_scale: float = 1.0,
    font_thickness: float = 1,
    font_face=cv2.FONT_HERSHEY_SIMPLEX,
    font_color_rgb: Tuple = (255, 255, 255),
    bg_color_rgb: Optional[Tuple] = None,
    outline_color_rgb: Optional[Tuple] = None,
    line_spacing: float = 1,
):
    """
    Adds text (including multi line text) to images.
    You can also control background color, outline color, and line spacing.

    outline color and line spacing adopted from: https://gist.github.com/EricCousineau-TRI/596f04c83da9b82d0389d3ea1d782592
    """
    OUTLINE_FONT_THICKNESS = 3 * font_thickness

    im_h, im_w = image_rgb.shape[:2]
    lines_to_print = []
    # for line in label.splitlines():
    for item in label:
        if "\n" in item:
            for i in item.splitlines():
                lines_to_print.append(i)
        else:
            lines_to_print.append(item)
    for line in lines_to_print:

        x, y = top_left_xy

        # ====== get text size
        if outline_color_rgb is None:
            get_text_size_font_thickness = font_thickness
        else:
            get_text_size_font_thickness = OUTLINE_FONT_THICKNESS

        (line_width, line_height_no_baseline), baseline = cv2.getTextSize(
            line,
            font_face,
            font_scale,
            get_text_size_font_thickness,
        )
        line_height = line_height_no_baseline + baseline

        if bg_color_rgb is not None and line:
            # === get actual mask sizes with regard to image crop
            if im_h - (y + line_height) <= 0:
                sz_h = max(im_h - y, 0)
            else:
                sz_h = line_height

            if im_w - (x + line_width) <= 0:
                sz_w = max(im_w - x, 0)
            else:
                sz_w = line_width

            # ==== add mask to image
            if sz_h > 0 and sz_w > 0:
                bg_mask = np.zeros((sz_h, sz_w, 3), np.uint8)
                bg_mask[:, :] = np.array(bg_color_rgb)
                image_rgb[
                    y : y + sz_h,
                    x : x + sz_w,
                ] = bg_mask

        # === add outline text to image
        if outline_color_rgb is not None:
            image_rgb = cv2.putText(
                image_rgb,
                line,
                (x, y + line_height_no_baseline),  # putText start bottom-left
                font_face,
                font_scale,
                outline_color_rgb,
                OUTLINE_FONT_THICKNESS,
                cv2.LINE_AA,
            )
        # === add text to image
        image_rgb = cv2.putText(
            image_rgb,
            line,
            (x, y + line_height_no_baseline),  # putText start bottom-left
            font_face,
            font_scale,
            font_color_rgb,
            font_thickness,
            cv2.LINE_AA,
        )
        top_left_xy = (x, y + int(line_height * line_spacing))

    return image_rgb


class MessageClip:
    def __init__(self, start_time, filename, image=[], bounding_rect=(0, 0, 0, 0)):
        self.start_time = start_time
        self.filename = Path(filename).name
        self.end_time = None
        self.text = None
        self.user = None
        self.donation = None
        self.color = None
        self.color_mean = 0

        if not len(image):
            # no superchat found
            self.super_chat = False
            self.image = self.create_chat_image()
            self.text = "\n"
        else:
            self.super_chat = True
            self.image = image
            # self.color = self.get_superchat_color()

        self.bounding_rect = bounding_rect

    def __eq__(self, obj):
        # return isinstance(obj, MessageClip) and self.is_same_image(obj)
        return isinstance(obj, MessageClip) and self.is_same_image2(obj)

    def is_same_image2(self, obj):
        i1 = Image.fromarray(self.image)
        i2 = Image.fromarray(obj.image)
        h1 = imagehash.average_hash(i1)
        h2 = imagehash.average_hash(i2)
        cutoff = 5  # need to tune this variable
        # 0 means the same, 32 means not similar, 64 means negative image
        return (h2 - h1) < cutoff

    def get_superchat_color(self):
        # valid colors are
        # BLUE, GREEN, YELLOW, ORANGE, PINK, RED
        if not self.super_chat:
            self.color = None
            return
        color_section = self.image.copy()
        color_section = color_section[30:80, 240:330]
        self.color_swatch = color_section
        save_image(color_section, "color_section.png", hsv=False)
        image = cv2.cvtColor(color_section, cv2.COLOR_BGR2HSV)
        image_color = np.average(image, axis=(0, 1))
        image_color = tuple((int(i) for i in image_color))
        self.color_mean = str(image_color)
        image_color = image_color[0]
        #

        # the key in the dict shows which set of colors should be used
        # looks like colors changed around WW100
        color_thresholds = {
            0: [
                {"name": "RED", "hue": 10},
                {"name": "ORANGE", "hue": 20},
                {"name": "YELLOW", "hue": 40},
                {"name": "GREEN", "hue": 90},
                {"name": "BLUE", "hue": 120},
                {"name": "PINK", "hue": 180},
            ],
            100: [
                {"name": "ORANGE", "hue": 10},
                {"name": "YELLOW", "hue": 25},
                {"name": "GREEN", "hue": 85},
                {"name": "BLUE", "hue": 95},
                {"name": "PINK", "hue": 170},
                {"name": "RED", "hue": 180},
            ],
        }
        episode_type = 100  # how to figure this out
        for color in color_thresholds[episode_type]:
            if image_color <= color["hue"]:
                self.color = color["name"]
                break
        if self.color is None:
            self.color = "NOCOLOR"
        print(self.color)
        x = 1 + 1  # here for breakpoint

    def get_text_from_superchat(self):
        # need to test if either of these works better on which color messages
        # other options to fix that
        # message = remove_avatar(message)
        # ocr_text(message)
        if not self.super_chat:
            return
        if self.color in ["BLUE", "GREEN", "YELLOW"]:
            text_color = "black"
        else:
            text_color = "white"
        all_text = read_text_from_image(self.image, self.color, text_color)
        text = [s for s in all_text.splitlines() if s.strip()]

        if len(text) == 1:
            self.user = text[0]
        elif len(text) == 2:
            self.user = text[0]
            self.donation = text[1]
        elif len(text) > 2:
            self.user = text[0]
            self.donation = text[1]
            self.text = "\n".join(text[2:])
            print("hi")

    def set_end_time(self, end_time):
        if end_time > self.start_time:
            self.end_time = end_time

    def create_chat_image(self):
        img = np.zeros((500, 500, 3), dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (50, 50)
        fontScale = 1
        color = (255, 0, 0)
        thickness = 2
        # Using cv2.putText() method
        img = cv2.putText(
            img,
            "No superchats found",
            org,
            font,
            fontScale,
            color,
            thickness,
            cv2.LINE_AA,
        )
        # save_image(img, "chat image.png", hsv=False)
        return img

    def is_same_image(self, other_image):
        # this should probably overwritten in the Clip class
        if other_image.image is None or self.image is None:
            print("images not properly passed to is_same_image")
            exit()
        im1 = self.image
        im2 = other_image.image
        # save_image(im1, "saving image1.png", hsv=False)
        # save_image(im2, "saving image2.png", hsv=False)

        my_result = tuple(
            map(
                lambda i, j: i - j,
                im1.shape,
                im2.shape,
            )
        )
        if abs(my_result[0]) < 10 and abs(my_result[1]) < 10:
            # the images are about the same sizes.
            # need to keep investigating
            # resize for bitwise comparison
            im1, im2 = make_same_shape(im1, im2)

            diff = cv2.bitwise_xor(im1, im2)
            # print(f"The mean of the xord diff is {diff.mean()} ")
            if diff.mean() < 15:
                # need a good number for this variable
                # looks like the image hasnt changed

                # lastly, check the user, donation and text
                # i know this is gross...
                self.text = self.get_text_from_superchat()
                other_image.text = other_image.get_text_from_superchat()
                if not self.text and not other_image.text:
                    # this means no text found on either
                    # probably a couple of chats in a row
                    return True
                elif not self.text or not other_image.text:
                    # this means text was found on one image, but not the other
                    # must be different
                    return False
                elif similar(self.text, other_image.text) < 0.5:
                    print("Found these texts similar\n{image1.text}\n{image2.text}")
                    return True
                else:
                    print(
                        "Found these texts different \n{image1.text}\n{image2.text}\n"
                    )
                    return False
            else:
                # this is likely a new super_chat.
                return False
                # save_image(
                # current_frame.image, "Superchat Image.png", hsv=False

    def __repr__(self):
        """Returns representation of the object"""
        return f"MessageClip - {self.start_time}:{self.end_time} - {self.super_chat}"

    def __str__(self):
        return f"MessageClip - {self.start_time}:{self.end_time} - {self.super_chat}"


# class RegularChatClip(Clip):
#     def __init__(self, start_time):
#         self.start_time = start_time

#         # this should never get a value
#         # using this as a hack to tell if its chat or superchat
#         self.image = self.create_chat_image()


# class SuperchatClip(Clip):
#     def __init__(self, start_time, image):
#         self.start_time = start_time
#         self.image = image
#         self.end_time = None  # can't be assigned when created
#         self.user = None
#         self.donation = None
#         self.color = None
#         self.text = None

#     def set_end_time(self, end_time):
#         if end_time > self.start_time:
#             self.end_time = end_time


class ProducerClip:
    def __init__(self, start_time, image):
        self.start_time = start_time
        self.image = image
        self.end_time = None  # can't be assigned when created
        self.producer = None
        self.beat_name = None


def make_same_shape(image1, image2):
    dest_shape = image2.shape
    image1 = cv2.resize(
        image1,
        (dest_shape[1], dest_shape[0]),
        interpolation=cv2.INTER_AREA,
    )
    return image1, image2


def is_new_message(current_frame, active_message_clip):
    if current_frame.super_chat:
        if not active_message_clip.super_chat:
            # new superchat found
            active_message_clip.set_end_time(current_time)
            active_message_clip = current_frame
            # save_image(current_frame.image, "Superchat Image.png", hsv=False)
            return True, current_frame, active_message_clip

        else:
            # there is already a superchat.  how do i know if it is the same as this one?

            if not current_frame == active_message_clip:
                # active_message_clip.set_end_time(current_time)
                # active_message_clip = current_frame
                # save_image(current_frame.image, "Superchat Image.png", hsv=False)
                return True, current_frame, active_message_clip
            else:
                return False, current_frame, active_message_clip

            # else:
            #     active_message_clip.set_end_time(current_time)
            #     message_clips.append(active_message_clip)
            #     # save_image(current_frame.image, "Superchat Image.png", hsv=False)
            #     return True, current_frame

    else:  # no superchat found
        if active_message_clip.super_chat:
            # this means that there was a superchat active, but now its just chat
            active_message_clip.set_end_time(current_time)
            active_message_clip = current_frame
            # save_image(current_frame.image, "Superchat Image.png", hsv=False)
            return True, current_frame, active_message_clip
        else:
            return False, current_frame, active_message_clip


def create_output_image(message):
    # this function creates the output image needed to compare the
    # text retrieved from the image to the actual image easily
    # should create a large rectangle (black?)
    # center the actual image on the left half of this rectangle
    # on the right half, should include the filename, user, donation,
    # and text retrieved

    output_image = np.ones((800, 600, 3), dtype=np.uint8)

    found_image = add_image_to_background(output_image, message.image)
    found_text = output_image
    text_to_add = [
        message.filename,
        message.color,
        message.color_mean,
        "original shape: " + str(message.image.shape),
        str(message.start_time) + ":" + str(message.end_time),
        message.user,
        message.donation,
        message.text,
    ]
    found_text = add_text_to_image(
        found_text,
        text_to_add,
    )
    # message_text = add_text_to_image(
    #     found_text,
    #     message.text,
    #     top_left_xy=(10, 30),
    # )
    found_image, found_text = make_same_shape(found_image, found_text)
    return cv2.hconcat([found_image, found_text])


def create_color_folders(base_folder):
    colors = ["BLUE", "GREEN", "ORANGE", "YELLOW", "PINK", "RED", "NOCOLOR"]
    for color in colors:
        target = Path(base_folder) / color
        target.mkdir(parents=True, exist_ok=True)


def test_find_message_function_speed():
    prefix = "WW100"
    file_list = get_file_list(f"temp_images/screengrabs/{prefix}/")

    funcs_to_test = [find_superchat_in_image2, find_superchat_in_image]
    for func in funcs_to_test:
        super_chat_timers = []
        no_super_chat_timers = []
        for f in file_list:
            img = cv2.imread(f)
            start = timeit.default_timer()
            message = func(img, f, 0)
            stop = timeit.default_timer()
            timer = stop - start
            if message.super_chat:
                super_chat_timers.append(timer)
            else:
                no_super_chat_timers.append(timer)
        avg1 = sum(super_chat_timers) / len(super_chat_timers)
        avg2 = sum(no_super_chat_timers) / len(no_super_chat_timers)
        print(f"Average execution time if superchat found: {avg1}")
        print(f"Average execution time if superchat NOT found: {avg2}")


if __name__ == "__main__":
    # test_find_message_function_speed()
    t = time.localtime()
    start_time = time.strftime("%H:%M:%S", t)
    print(start_time)
    # extract_images_from_video()
    #    FILE = "WW091"
    FILES = [
        # "WW100",
        # "WW035",
        # "WW036",
        # "WW037",
        # "WW038",
        # "WW039",
        "WW076",
        "WW099",
    ]
    for prefix in FILES:
        create_color_folders(f"temp_images/output/{prefix}/")
        file_list = get_file_list(f"temp_images/screengrabs/{prefix}/")
        if file_list is None:
            print(f"No files found for {prefix}")
            continue
        message_clips = []
        producer_clips = []

        active_message_clip = MessageClip(
            start_time=0, filename=""
        )  # shouldn't ever start immediately with superchat
        potential_active_message_clip = MessageClip(start_time=0, filename="")
        active_producer_clip = None  # should always start as none?
        current_time = 0  # seconds

        MAX_TIME_TO_BE_ACTIVE = 4
        frame_counter = 0
        for f in file_list:

            current_time += 1  # position in the video.  1 sec = 30 frames (need to verify per video)
            print(f"checking for superchats for {f} ")
            if active_message_clip.super_chat:
                # i have an active super_chat. cut out the bounding rect from the current
                # frame and compare that to active message.  if its the same then can ignore everything else
                new_image = crop_image_to_rect(f, active_message_clip.bounding_rect)
                new_image_clip = MessageClip(start_time=0, filename=f, image=new_image)
                # shouldn't ever start immediately with superchat
                # save_image(new_image, "new_image.png", hsv=False)
                if active_message_clip == new_image_clip:
                    continue
            current_frame = find_message_in_image(f, current_time)

            if current_frame.super_chat or active_message_clip.super_chat:
                cf = current_frame.image
                af = active_message_clip.image
                paf = potential_active_message_clip.image

                if current_frame != active_message_clip:

                    print("current NO MATCH FOR active")
                    if current_frame == potential_active_message_clip:
                        print(
                            f"current MATCHES potential:  frame counter = {str(frame_counter)}"
                        )
                        frame_counter += 1
                        if frame_counter == MAX_TIME_TO_BE_ACTIVE:
                            frame_counter = 0
                            print("potential IS BECOMING active")
                            active_message_clip.set_end_time(
                                current_time - MAX_TIME_TO_BE_ACTIVE
                            )
                            message_clips.append(active_message_clip)
                            active_message_clip = potential_active_message_clip

                            start = timeit.default_timer()
                            active_message_clip.get_superchat_color()
                            stop = timeit.default_timer()
                            print(
                                f"Getting super chat color took {(stop-start)*1000} ms"
                            )

                            start = timeit.default_timer()
                            active_message_clip.get_text_from_superchat()
                            stop = timeit.default_timer()
                            print(f"Getting text took {(stop-start)*1000} ms")

                    else:
                        frame_counter = 1
                        potential_active_message_clip = current_frame
                        print(print("current IS NEW potential"))

        count = 0
        # just using to time the process
        # started at 11:28
        t = time.localtime()
        end_time = time.strftime("%H:%M:%S", t)
        print(end_time)

        rows = []

        for message in message_clips:
            if message.text is None or message.text == "\n":
                message.get_text_from_superchat()
            if message.super_chat and message.text:
                # file.write(message.text)

                text_to_add = [
                    message.filename,
                    message.color,
                    message.color_mean,
                    message.user,
                    message.donation,
                ]
                text = [s for s in message.text.splitlines() if s.strip()]
                text_to_add.extend(text)
                rows.append(text_to_add)
                count += 1
                output_image = create_output_image(message)
                # save_image(
                #     output_image,
                #     f"{prefix}/{message.color}/unique found message {str(count)}.png",
                #     hsv=False,
                # )
                save_image(
                    message.image,
                    f"{prefix}/{prefix}_{str(count)}.png",
                    hsv=False,
                )
        # file = open(f"temp_images/output/{FILE}/text_results.txt", "a")
        filename = f"temp_images/output/{prefix}/text_results.csv"

        # writing to csv file
        fields = "filename", "color", "color_mean", "user", "donation", "text"
        with open(filename, "w") as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)

            # writing the fields
            csvwriter.writerow(fields)

            # writing the data rows
            csvwriter.writerows(rows)


# time was 04:45:43 when started
