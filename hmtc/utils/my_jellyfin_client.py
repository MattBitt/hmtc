from dataclasses import dataclass
import time
from jellyfin_apiclient_python import JellyfinClient
from hmtc.config import init_config
from hmtc.components.shared.sidebar import VERSION
from loguru import logger


config = init_config()
# not sure why but this seems to work better if its a global
client = JellyfinClient()


@dataclass
class MyJellyfinClient:
    session: str = None
    session_id: str = None
    position: int = 0
    user: str = None
    media_item: dict = None
    supports_media_control: bool = False
    supports_remote_control: bool = False
    is_playing: bool = False
    is_connected: bool = False
    has_active_user_session: bool = False
    play_status: str = "stopped"

    def __post_init__(self):
        url = config["jellyfin"]["url"]
        self.user = config["jellyfin"]["user"]
        password = config["jellyfin"]["password"]

        client.config.app("hmtc", VERSION, "zeus", VERSION)
        client.config.data["auth.ssl"] = True
        client.auth.connect_to_address(url)
        client.auth.login(url, self.user, password)
        credentials = client.auth.credentials.get_credentials()
        try:
            s = credentials["Servers"]
        except Exception as e:
            logger.error(f"Credential Error: {credentials} error: {e}")
            return self

        if s == []:
            logger.error("No Jellyfin Servers found")
            return self

        self.is_connected = True

        client.authenticate(credentials, discover=False)
        if client.logged_in:
            self.session = self.get_current_session()
            if self.session is None:
                logger.debug("No active session found.")
            else:
                self.session_id = self.session["Id"]
                self.has_active_user_session = True
                self.supports_media_control = self.session["SupportsMediaControl"]
                self.supports_remote_control = self.session["SupportsRemoteControl"]

                if "NowPlayingItem" in self.session.keys():
                    self.media_item = self.session["NowPlayingItem"]
                    self.position = (
                        int(self.session["PlayState"]["PositionTicks"]) / 10_000_000
                    )
                    self.play_status = (
                        "paused"
                        if self.session["PlayState"]["IsPaused"] == True
                        else "playing"
                    )
                else:
                    self.media_item = None
                    self.position = 0
                    self.play_status = "stopped"

        return self

    def get_current_session(self):
        for sess in client.jellyfin.sessions():
            if (
                sess["UserName"] == self.user
                and sess["Client"] != "hmtc"
                and sess["SupportsMediaControl"] == True
            ):
                return sess

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
                logger.debug("(WTF?)")
                # item = self.session["NowPlayingQueueFullItems"][0]
            except Exception as e:
                logger.debug(f"No item found in NowPlayingQueueFullItems  {e}")
                return None

            return {
                "jf_id": self.media_item["Id"],
                "title": self.media_item["Name"],
                "path": self.media_item["Path"],
                "status": self.play_status,
                "position": self.position,
                "tags": [],
                "type": item_type,
            }
        else:
            logger.debug("Nothing is playing right now.")
            return None

    def load_media_item(self, jellyfin_id):
        client.jellyfin.remote_play_media(
            id=self.session_id, item_ids=[jellyfin_id], command="PlayNow"
        )
        time.sleep(
            0.1
        )  # i think this is necessary to give jellyfin time to load the media
        self.pause()

    def pause(self):
        client.jellyfin.remote_pause(self.session_id)

    def play_pause(self):
        client.jellyfin.remote_playpause(self.session_id)

    def stop(self):
        client.jellyfin.remote_stop(self.session_id)


if __name__ == "__main__":
    jf = MyJellyfinClient()
    if jf.supports_media_control and jf.media_item is None:
        jf.load_media_item(jellyfin_id="6f6baa6a3bf619d667d5b1edb3677205")

    logger.debug("Initial Pause")
    jf.play_pause()
    time.sleep(2)

    logger.debug("Playing")
    jf.play_pause()
    time.sleep(2)

    logger.debug("Pausing")
    jf.pause()
    time.sleep(2)

    logger.debug("Playing")
    jf.play_pause()
    time.sleep(2)

    logger.debug("Stopping")
    jf.stop()
    print(jf.now_playing())
