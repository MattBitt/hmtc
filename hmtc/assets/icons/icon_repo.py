from enum import Enum


class Icons(Enum):
    ALBUM = "mdi-album"
    ARTIST = "mdi-account"
    BEAT = "mdi-music"
    CHANNEL = "mdi-format-list-bulleted"
    DELETE = "mdi-delete"
    DISC = "mdi-disc"
    DOMAIN = "mdi-google-circles-extended"
    EDIT = "mdi-pencil"
    FILE = "mdi-folder"
    HOME = "mdi-home"
    SANDBOX = "mdi-shovel"
    SEARCH = "mdi-magnify"
    SECTION = "mdi-rhombus-split"
    SERIES = "mdi-shape"
    SETTINGS = "mdi-cogs"
    SUPERCHAT = "mdi-chat"
    SUPERCHAT_SEGMENT = "mdi-segment"
    TOPIC = "mdi-book-open"
    TRACK = "mdi-music-clef-treble"
    USER = "mdi-account"
    VIDEO = "mdi-video"
    YOUTUBE_SERIES = "mdi-youtube"
    UP_BOX = "mdi-arrow-up-box"
    DOWN_BOX = "mdi-arrow-down-box"
    FINETUNER = "mdi-glasses"
    UNLOCK = 'mdi-axe'
    LOCK = 'mdi-bookmark-check-outline'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
