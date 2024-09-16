from dataclasses import dataclass
from jellyfin_apiclient_python import JellyfinClient
from hmtc.config import init_config
from hmtc.components.shared.sidebar import VERSION
from loguru import logger


config = init_config()


@dataclass
class MyJellyfinClient:
    client: JellyfinClient = None
    session: str = None
    supports_media_control: bool = False
    supports_remote_control: bool = False
    is_playing: bool = False
    position: int = 0
    play_status: str = None
    user: str = None
    media_item: dict = None

    def connect(self):

        url = config["jellyfin"]["url"]
        self.user = config["jellyfin"]["user"]
        password = config["jellyfin"]["password"]

        self.client = JellyfinClient()

        self.client.config.app("hmtc", VERSION, "zeus", VERSION)
        self.client.config.data["auth.ssl"] = True

        self.client.auth.connect_to_address(url)
        self.client.auth.login(url, self.user, password)
        credentials = self.client.auth.credentials.get_credentials()
        # need to check for empty credentials
        s = credentials["Servers"]
        # logger.debug(f"Found {len(s)} Jellyfin Servers")
        if s == []:
            logger.error("No Jellyfin Servers found")
            return None

        # not sure what this does 8-30-24
        # server = credentials["Servers"][0]
        # server["username"] = "matt"

        self.client.authenticate(credentials, discover=False)

        if self.client.logged_in:
            sessions_list = []

            total_sessions = len(self.client.jellyfin.sessions())

            for sess in self.client.jellyfin.sessions():
                if sess["UserName"] == self.user and sess["Client"] != "hmtc":
                    sessions_list.append(sess)
                    self.supports_media_control = sess["SupportsMediaControl"]
                    self.is_playing = sess["PlayState"]["CanSeek"]
                    self.supports_remote_control = sess["SupportsRemoteControl"]
                    if "NowPlayingItem" in sess.keys():
                        self.media_item = sess["NowPlayingItem"]
                        self.position = (
                            int(sess["PlayState"]["PositionTicks"]) / 10_000_000
                        )
                        self.play_status = (
                            "paused"
                            if sess["PlayState"]["IsPaused"] is True
                            else "playing"
                        )
            logger.debug(
                f"Current {self.user} sessions: {len(sessions_list)} of {total_sessions} total"
            )

            if len(sessions_list) == 1:
                logger.debug("One session found!")
                self.session = sessions_list[0]
            elif len(sessions_list) > 1:
                logger.debug("Multiple sessions found. Returning the first one")
                self.session = sessions_list[0]
            else:
                logger.debug("No sessions found")
                self.session = None
        else:
            logger.error("login failed")
            logger.error("Error Connecting to Jellyfin")

    def now_playing(self):
        if self.is_playing:
            # im not sure what the point of this is... 9/15/24
            path_str = self.media_item["Path"]
            if "inputs" in path_str:
                item_type = "input"
            else:
                item_type = "track"

            # i think this was my attempt at a 'tag' solution for jellyfin 9/15/24
            try:
                item = self.session["NowPlayingQueueFullItems"][0]
            except:
                logger.debug("No item found in NowPlayingQueueFullItems")
                return None

            return {
                "jf_id": self.media_item["Id"],
                "title": self.media_item["Name"],
                "path": self.media_item["Path"],
                "status": self.play_status,
                "position": self.position,
                "tags": item["Tags"],
                "type": item_type,
            }
        else:
            logger.debug("Nothing is playing right now.")
            return None


if __name__ == "__main__":
    jf = MyJellyfinClient()
    jf.connect()
    print(jf.now_playing())
