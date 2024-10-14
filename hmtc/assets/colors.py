from enum import Enum


# need to make sure to keep these in sync with styles.css
# using ERROR in VideoFilesInfoModal.vue
class Colors(Enum):
    PRIMARY = "#6A00F4"
    SECONDARY = "#532B88"
    ACCENT = "#BC00DD"
    ERROR = "#2D00F7"
    INFO = "#E500A4"
    SUCCESS = "#F20089"
    WARNING = "#FFB600"

    SURFACE = "#808080"
    BACKGROUND = "#0000FF"

    LIGHT = "#FF0000"
    DARK = "#00FF00"

    ONPRIMARY = "#000000"
    ONSURFACE = "#FFFFFF"
    ONLIGHT = "#000000"
    ONDARK = "#FFFFFF"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
