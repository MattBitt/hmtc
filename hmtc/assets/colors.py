from enum import Enum


class Colors(Enum):
    LIGHT = "#FFAB91"
    PRIMARY = "#FF5722"
    DARK = "#BF360C"
    ONLIGHT = "#000000"
    ONPRIMARY = "#000000"
    ONDARK = "#FFFFFF"
    SURFACE = "#808080"
    BACKGROUND = "#F0FF0F"
    ERROR = "#B00020"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
