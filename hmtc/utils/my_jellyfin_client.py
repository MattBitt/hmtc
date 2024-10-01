import time
from dataclasses import dataclass

from jellyfin_apiclient_python import JellyfinClient
from loguru import logger

from hmtc.config import init_config

config = init_config()
# not sure why but this seems to work better if its a global
client = JellyfinClient()


@dataclass
class MyJellyfinClient:
    session: str = None
    session_id: str = None
    position: int = 0
    user: str = None
    user_id: str = None
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

        client.config.app("hmtc", "0.0.0.0.0", "zeus", "0.0.0.0.0")
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
                self.user_id = self.session["UserId"]

        return self

    def get_playing_status_from_jellyfin(self):
        if self.session is None:
            logger.error(f"No active session found.")
            return None

        if "NowPlayingItem" in self.session.keys():
            self.media_item = self.session["NowPlayingItem"]
            self.position = int(self.session["PlayState"]["PositionTicks"]) / 10_000_000
            self.play_status = (
                "paused" if self.session["PlayState"]["IsPaused"] == True else "playing"
            )
            return {
                "jf_id": self.media_item["Id"],
                "title": self.media_item["Name"],
                "path": self.media_item["Path"],
                "status": self.play_status,
                "position": self.position,
            }
        else:
            self.media_item = None
            self.position = 0
            self.play_status = "stopped"
            return None

    def get_current_session(self):
        for sess in client.jellyfin.sessions():
            if "UserName" in sess.keys():
                if (
                    sess["UserName"] == self.user
                    and sess["Client"] != "hmtc"
                    and sess["SupportsMediaControl"] == True
                ):
                    return sess
            else:
                logger.debug(f"Session: {sess} doesn't have username")

    # def now_playing(self):
    #     pass
    #     if self.is_playing:
    #         # im not sure what the point of this is... 9/15/24
    #         path_str = self.media_item["Path"]
    #         if "inputs" in path_str:
    #             item_type = "input"
    #         else:
    #             item_type = "track"

    #         # i think this was my attempt at a 'tag' solution for jellyfin 9/15/24
    #         try:
    #             logger.debug("(WTF?)")
    #             # item = self.session["NowPlayingQueueFullItems"][0]
    #         except Exception as e:
    #             logger.debug(f"No item found in NowPlayingQueueFullItems  {e}")
    #             return None

    #         return {
    #             "jf_id": self.media_item["Id"],
    #             "title": self.media_item["Name"],
    #             "path": self.media_item["Path"],
    #             "status": self.play_status,
    #             "position": self.position,
    #             "tags": [],
    #             "type": item_type,
    #         }
    #     else:
    #         logger.debug("Nothing is playing right now.")
    #         return None

    def load_media_item(self, jellyfin_id):
        client.jellyfin.remote_play_media(
            id=self.session_id, item_ids=[jellyfin_id], command="PlayNow"
        )
        time.sleep(
            0.1
        )  # i think this is necessary to give jellyfin time to load the media
        # self.pause()

    def pause(self):
        client.jellyfin.remote_pause(self.session_id)

    def play_pause(self):
        client.jellyfin.remote_playpause(self.session_id)

    def stop(self):
        client.jellyfin.remote_stop(self.session_id)

    def search_media(self, query):
        return client.jellyfin.search_media_items(query)

    def seek_to(self, position):
        client.jellyfin.remote_seek(self.session_id, position * 10_000)


if __name__ == "__main__":
    jf = MyJellyfinClient()
