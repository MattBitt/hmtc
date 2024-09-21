from enum import Enum


# need to make sure to keep these in sync with styles.css
class Colors(Enum):
    LIGHT = "#c8b1e4"
    PRIMARY = "#9b72cf"
    DARK = "#532b88"

    SURFACE = "#808080"
    BACKGROUND = "#F0FF0F"
    ERROR = "#00B020"
    WARNING = "#FFC107"
    ONLIGHT = "#000000"
    ONPRIMARY = "#000000"
    ONDARK = "#FFFFFF"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
