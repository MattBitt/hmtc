from enum import Enum


class Icons(Enum):
    ALBUM = "mdi-album"
    ARTIST = "mdi-account"
    BEAT = "mdi-music"
    CHANNEL = "mdi-format-list-bulleted"
    DELETE = "mdi-delete"
    DISC = "mdi-disc"
    DOMAIN = "mdi-google-circles-extended"
    DOWN_BOX = "mdi-arrow-down-box"
    DOWNLOAD = 'mdi-download'
    EDIT = "mdi-pencil"
    FILE = "mdi-folder"
    FINETUNER = "mdi-glasses"
    HOME = "mdi-home"
    LOAD_MEDIA = "mdi-cards-playing-outline"
    LOCK = "mdi-bookmark-check-outline"
    PLAYPAUSE = "mdi-play-pause"
    REFRESH = "mdi-refresh"
    SANDBOX = "mdi-shovel"
    SEARCH = "mdi-magnify"
    SECTION = "mdi-rhombus-split"
    SERIES = "mdi-shape"
    SETTINGS = "mdi-cogs"
    SUPERCHAT = "mdi-chat"
    SUPERCHAT_SEGMENT = "mdi-segment"
    TOPIC = "mdi-book-open"
    TRACK = "mdi-music-clef-treble"
    UNLOCK = "mdi-axe"
    UNIQUE = "mdi-cookie"
    UP_BOX = "mdi-arrow-up-box"
    USER = "mdi-account"
    VIDEO = "mdi-video"
    YOUTUBE_SERIES = "mdi-youtube"
    STATS = "mdi-space-station"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
