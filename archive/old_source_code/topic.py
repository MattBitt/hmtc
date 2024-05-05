import re
from collections import Counter
from pathlib import Path

import cv2
import imagehash
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from matplotlib import cbook
from matplotlib.colors import LightSource
from PIL import Image
from sklearn.cluster import KMeans
from utils import crop_to_contour


class Topic:
    CLUSTERS = 1

    def __init__(self, original_image, contour=None):
        if original_image is None:
            raise IOError
        self.original_image = original_image
        # these colors signify the threshold(s) that produced the contour
        # should be able to use these to help figure out the superchat color
        if contour is not None:
            self.contour = contour
            self.image = crop_to_contour(original_image, self.contour)
        else:
            self.image = original_image
        self.user = None
        self.donation = None
        self.text = None
        self.image_for_ocr = None
        self.words = None
        self.image_hash = self.compute_image_hash()
        #  self.color = self.find_superchat_color()

        # self.read_text_from_image()

    def find_superchat_color(self):
        # img = cv2.cvtColor(self.image.copy(), cv2.COLOR_BGR2RGB)

        img = cv2.resize(self.image.copy(), (0, 0), fx=0.5, fy=0.5)
        img = img.reshape((img.shape[0] * img.shape[1], 3))
        # kmeans = KMeans(n_clusters=self.CLUSTERS, n_init="auto")
        kmeans = KMeans(
            n_clusters=self.CLUSTERS,
            # init="k-means++",
            n_init="auto",
            # max_iter=300,
        )
        kmeans.fit(img)
        self.COLORS = kmeans.cluster_centers_

        width = 300
        palette = np.zeros((50, width, 3), np.uint8)
        steps = width / self.COLORS.shape[0]
        for idx, centers in enumerate(self.COLORS):
            palette[:, int(idx * steps) : (int((idx + 1) * steps)), :] = centers

        colors = np.rint(self.COLORS)
        # count = 0

        # if len(colors) == 1:
        #    colors = (colors[0], colors[0])
        # only need to loop if more than 1 cluster is needed.  might be better off with
        # one cluster total
        # for color in colors:
        # count += 1
        rgb = [
            [colors[0]]
        ]  # increasing the dimension of array so that opencv can work with it
        array = np.array(rgb, np.uint8)  # defining an array with uint8 type
        hsv = cv2.cvtColor(array, cv2.COLOR_RGB2HSV)  # converting RGB to HSV
        h = hsv[0][0][0]

        if 20 <= h <= 34:
            color_name = "blue"
        elif 35 <= h <= 60:
            color_name = "green"
        elif 91 <= h <= 102:
            color_name = "yellow"
        elif 103 <= h <= 114:
            color_name = "orange"
        elif 115 <= h <= 126:
            color_name = "red"

        elif 127 <= h <= 137:
            color_name = "pink"

        else:
            color_name = "not found!!!"
        # print(f"superchat color = {found_colors}")
        self.color = color_name
        return palette, color_name
        # save labels

        # self.LABELS = kmeans.labels_

        # # returning after converting to integer from float
        # return self.COLORS.astype(int)

    def compute_image_hash(self):
        i1 = Image.fromarray(self.image)
        return imagehash.average_hash(i1)

    def __eq__(self, obj):
        return isinstance(obj, Topic) and self.is_same_image(obj)

    def is_same_image(self, obj):
        # the cutoff should be high.  if it doesn't meet this
        # then its definietly not the same image
        # if its less than that, though probably need to analyze the text
        # to find out if it has changed
        if self.image is None and obj.image is None:
            return True
        if self.image is None or obj.image is None:
            return False
        cutoff = 8  # need to tune this variable
        # 0 means the same, 32 means not similar, 64 means negative image
        return (self.image_hash - obj.image_hash) < cutoff

    def read_text_from_image(self):
        self.find_superchat_color()
        if self.color in ["blue", "green", "yellow"]:
            self.text_color = "black"
        else:
            self.text_color = "white"
        self.prep_image_for_ocr()
        if self.image_for_ocr is None:
            raise IOError
        # read text from whole image
        all_text = pytesseract.image_to_string(self.image_for_ocr, config="--psm 6")
        # split into newlines, discarding blanks
        text = [s for s in all_text.splitlines() if s.strip()]
        # text is split into newlines
        # cant assume that username will always only have 1 line
        # try to find the donation by looking for currency symbols or
        # ".00"

        if len(text) == 1:
            self.user = text[0]
        elif len(text) == 2:
            self.user = text[0]
            self.donation = text[1]
        elif len(text) > 2:
            for idx, line in enumerate(text):
                # need to look for numbers/currency symbols, etc.
                x = re.search(r"\.\d\d", line)
                if x:
                    # probably found the donation
                    self.user = "\n".join(text[:idx])
                    self.donation = line
                    self.text = "\n".join(text[idx + 1 :])
                    self.user = self.clean_up_text(self.user)
                    self.words = self.extract_key_words(self.text)
            # couldn't find a donation line for sure, so take the best guess
            self.user = text[0]
            self.donation = text[1]
            self.text = "\n".join(text[2:])
            self.user = self.clean_up_text(self.user)
            self.words = self.extract_key_words(self.text)
            # print(self.words)

    def clean_up_text(self, text):
        bad_chars = r"\"$%&\'()*+,-.:;<=>?@[\\]_|}~¢£¥©®°—‘’“”€™!#"
        bad_chars = sorted(list(set(bad_chars)))
        bad_chars.extend(["| ", " :", "_ ", "\\ ", ", ", "Â", "©", " .", "* ", "] "])
        for char in bad_chars:
            if char in text:
                text = text.replace(char, "").strip()

        return text

    def extract_key_words(self, source_text):
        if source_text is None:
            return None
        text = self.clean_up_text(source_text)
        text = text.replace("\n", " ").lower()
        return text

    def remove_avatar(self, image):
        # don't remove the avatar until its time to read the text
        new_image = image.copy()
        # cropped = new_image[0:80, 0:90]
        # gray_image = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        # edges = cv2.Canny(gray_image, 100, 200)
        # img2 = cv2.merge((edges, edges, edges))
        # next_image = cv2.bitwise_and(cropped, img2)
        # contours, hierarchy = cv2.findContours(
        #     image=edges,
        #     mode=cv2.RETR_EXTERNAL,
        #     method=cv2.CHAIN_APPROX_NONE,
        # )

        # drawn_contours = cv2.drawContours(
        #     image=edges.copy(),
        #     contours=contours,
        #     contourIdx=-1,
        #     color=(0, 255, 0),
        #     thickness=2,
        #     lineType=cv2.LINE_AA,
        # )
        # cv2.imwrite("test_images/output/remove_avatar/contours.png", next_image)

        # avatar = cv2.HoughCircles(
        #     edges,
        #     cv2.HOUGH_GRADIENT,
        #     1.3,
        #     100,
        #     param1=80,
        #     param2=140,
        #     minRadius=40,
        #     maxRadius=90,
        # )
        # if avatar is not None:
        #     avatar = np.round(avatar[0, :]).astype("int")
        #     for (x, y, r) in avatar:

        #         cv2.circle(avatar, (x, y), r, (0, 255, 0), 2)
        #         cv2.imwrite("test_images/output/remove_avatar/avatar.png", new_image)
        #         print(x, y, r)
        # # this makes this function useless.  return the updated image after tessting
        # return image

    def prep_image_for_ocr(self):
        if self.image is None:
            raise IOError
        im = self.image.copy()
        no_avatar = remove_avatar(im)
        scale_percent = 220
        width = int(no_avatar.shape[1] * scale_percent / 100)
        height = int(no_avatar.shape[0] * scale_percent / 100)
        dim = (width, height)

        resized = cv2.resize(no_avatar, dim, interpolation=cv2.INTER_AREA)

        gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        if self.text_color == "white":  # always use white background/black text
            gray_image = cv2.bitwise_not(gray_image)

        if self.color == "orange":
            # no idea where these arguments came from...
            kernel = np.ones((5, 5), np.uint8)
            thresh = cv2.dilate(gray_image, kernel, iterations=1)
            thresh = cv2.adaptiveThreshold(
                thresh, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 11
            )

            # The first parameter is the original image,
            # kernel is the matrix with which image is
            # convolved and third parameter is the number
            # of iterations, which will determine how much
            # you want to erode/dilate a given image.

            # thresh = cv2.erode(thresh, kernel, iterations=1)
        else:
            ret, thresh = cv2.threshold(gray_image, 120, 255, cv2.THRESH_BINARY)

        self.image_for_ocr = thresh

    def __repr__(self) -> str:
        return f"Topic {str(self.user)} --> {self.donation} --> {self.text}"


def histogram_plot(data):
    # Load and format data
    dem = cbook.get_sample_data("jacksboro_fault_dem.npz", np_load=True)
    z = dem["elevation"]
    x, y, z = data[:, 0], data[:, 1], data[:, 2]
    ncols = 3
    nrows = x.shape[0]
    x = np.linspace(0, 255, ncols)
    y = np.linspace(0, 255, nrows)
    x, y = np.meshgrid(x, y)

    # region = np.s_[5:50, 5:50]
    # x, y, z = x[region], y[region], z[region]

    # Set up plot
    fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

    ls = LightSource(270, 45)
    # To use a custom hillshading mode, override the built-in shading and pass
    # in the rgb colors of the shaded surface calculated from "shade".
    # rgb = ls.shade(z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode="soft")
    surf = ax.plot_surface(
        x,
        y,
        z,
        rstride=1,
        cstride=1,
        linewidth=0,
        antialiased=False,
        shade=False,
    )

    plt.savefig("test_images/output/topics_from_video/by_color/hillside.png")


def superchat_colors(color_name):
    source_folder = Path(f"test_images/output/topics_from_video/by_color/{color_name}/")
    target_folder = Path(
        f"test_images/output/topics_from_video/by_color/{color_name}_palattes/"
    )
    if not target_folder.exists():
        target_folder.mkdir(parents=True)
    colors_found = []
    for file in source_folder.iterdir():
        im = cv2.imread(str(file))
        t = Topic(im)
        palette, color = t.find_superchat_color()
        if color != color_name:
            print(f"{file}: {color}")
            fname = str(target_folder / (str(file.stem) + ".png"))
        else:
            fname = str(target_folder / ("match_" + str(file.stem) + ".png"))
        # cv2.imwrite(fname, palette)
        colors_found.append(color)
        # print(f"color={color}")
        # colors = np.rint(colors)
        # for color in colors:
        #     rgb = [
        #         [color]
        #     ]  # increasing the dimension of array so that opencv can work with it
        #     array = np.array(rgb, np.uint8)  # defining an array with uint8 type
        #     hsv_frame = cv2.cvtColor(array, cv2.COLOR_RGB2HSV)  # converting RGB to HSV
        #     palettes.append(hsv_frame)

    counter = Counter(colors_found)

    print(counter)
    # hsv = np.reshape(np.asarray(palettes), (-1, 3))
    # h, s, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    # print(f"{color_name}: = {str(h.mean())}")
    # creating plotting data
    # Ab_hist = cv2.calcHist(d, [0], None, [256], [0, 256])
    # xaxis = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    # yaxis = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # # plotting
    # plt.plot(xaxis, yaxis)
    # plt.xlabel("X")
    # plt.ylabel("Y")

    # # saving the file.Make sure you
    # # use savefig() before show().

    # hist, bin_edges = np.histogram(d, density=True)
    # _ = plt.hist(d, bins="auto")  # arguments are passed to np.histogram
    # plt.title("Histogram with 'auto' bins")
    # plt.savefig("squares.png")
    # g = np.reshape(d, (3, 3))
    # cv2.imwrite(str(source_folder / "hist.png"), b_hist)
    # f, indexes, counts = np.unique(g, return_index=True, return_counts=True, axis=0)
    # print(sorted(f.tolist()))


def crop_avatar(color_name):
    source_folder = Path(f"test_images/output/topics_from_video/by_color/{color_name}/")
    target_folder = Path("test_images/output/crop_avatar")
    if not source_folder.exists():
        raise IOError
    if not target_folder.exists():
        target_folder.mkdir(parents=True)

    for file in source_folder.iterdir():
        im = cv2.imread(str(file))
        cropped = im[0:85, 0:95]
        fname = str(target_folder / (str(file.stem) + ".png"))
        cv2.imwrite(fname, cropped)


def remove_avatar(image):
    # source_folder = Path("test_images/sample_topics_grabbed")
    # target_folder = Path("test_images/output/remove_avatar")
    # if not source_folder.exists():
    #     raise IOError
    # if not target_folder.exists():
    #     target_folder.mkdir(parents=True)

    # for file in sorted(source_folder.iterdir()):
    # im = cv2.imread(str(file))
    # take small slice of header of image to find the overall color
    # format for slicing is [y_start:y_end, x_start:x_end]
    cropped = image.copy()[10:60, 5:20]
    cropped = cropped.reshape((cropped.shape[0] * cropped.shape[1], 3))

    kmeans = KMeans(
        n_clusters=1,
        # init="k-means++",
        n_init="auto",
        # max_iter=300,
    )
    kmeans.fit(cropped)
    # print(str(file) + ":" + str(kmeans.cluster_centers_))
    color = kmeans.cluster_centers_[0]
    image[0:90, 0:90] = color
    return image
    # fname = str(target_folder / (str(file.stem) + ".png"))
    # cv2.imwrite(fname, im)


if __name__ == "__main__":
    color_name = "yellow"

    # superchat_colors(color_name)
    # crop_avatar(color_name)
    # find_dominant_color()
