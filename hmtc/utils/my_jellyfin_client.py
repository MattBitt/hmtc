import time
from collections import defaultdict
from dataclasses import InitVar, dataclass, field

from jellyfin_apiclient_python import JellyfinClient
from loguru import logger

from hmtc.config import init_config

config = init_config()
# not sure why but this seems to work better if its a global
try:
    client = JellyfinClient()

except Exception as e:
    logger.error(f"Error creating JellyfinClient (in global state): {e}")


@dataclass
class MyJellyfinClient:
    user: str = field(init=False)
    url: str = field(init=False)
    password: str = field(init=False)

    is_connected: bool = False
    active_session: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict))
    can_seek: bool = False
    found_users_sessions: bool = False

    session_id: str = None
    position: int = 0
    user_id: str = None
    media_item: dict = None
    supports_media_control: bool = False
    supports_remote_control: bool = False
    is_playing: bool = False

    play_status: str = "stopped"

    def __post_init__(self):
        self.user = config["jellyfin"]["user"]
        self.url = config["jellyfin"]["url"]
        self.password = config["jellyfin"]["password"]

        try:
            self.configure_client()
        except Exception as e:
            logger.error(f"Error connecting to Jellyfin: {e}")

        return self

    def has_active_session(self):
        # this is probably the wrong way to do this....
        if type(self.active_session) == defaultdict:
            logger.debug("Checking for active session and DID NOT find one.")
            return False
        else:
            logger.debug("Checking for active session and FOUND ONE!.")
            return True

    def configure_client(self):
        # no idea what these values are supposed to be used for.
        client.config.app("hmtc", "0.0.0.0.0", "zeus", "0.0.0.0.0")
        client.config.data["auth.ssl"] = True

    def connect(self):
        try:
            client.auth.connect_to_address(self.url)
            client.auth.login(self.url, self.user, self.password)
            self.is_connected = True
        except Exception as e:
            self.is_connected = False
            logger.error(f"Error connecting to Jellyfin in MyJellyfinClient: {e}")

        try:
            credentials = client.auth.credentials.get_credentials()
            client.authenticate(credentials, discover=False)
            if len(credentials["Servers"]) == 0:
                logger.error("No Jellyfin Servers found")

        except Exception as e:
            logger.error(f"Credential Error: {credentials} error: {e}")

        try:
            self.set_active_session()

        except Exception as e:
            logger.error(f"Error setting active section: {e}")
            return None

        if self.active_session is not None:
            self.session_id = self.active_session["Id"]
            self.supports_media_control = self.active_session["SupportsMediaControl"]
            self.supports_remote_control = self.active_session["SupportsRemoteControl"]
            self.user_id = self.active_session["UserId"]

    def set_active_session(self):
        # this gets controllable sessions, but Roku is not controllable
        sessions = client.jellyfin.get_sessions()
        if len(sessions) == 1:
            if sessions[0].get("UserName", "") == self.user:
                logger.debug("Only one session found. Skipping the nonsense.")
                # logger.debug(f"Session: {sessions[0]}")
                self.active_session = sessions[0]
                self.can_seek = True
                self.found_users_sessions = True
                return
        else:

            logger.debug(f"Number of sessions found: {len(sessions)}")
            for s in sessions:
                logger.debug(f"Session: {s}")

        user_sessions = [
            x["UserName"]
            for x in sessions
            if x.get("UserName", "") == self.user and x.get("Client", "") != "hmtc"
        ]
        if len(user_sessions) == 0:
            # lets check the rest of the sessions
            # all_sessions = [
            #     x for x in client.jellyfin.sessions() if x.get("Client", "") != "hmtc"
            # ]
            # # I think that the roku sessions will be here
            # # logger.debug(f"Number of all sessions found: {len(all_sessions)}")
            # if len(all_sessions) > 0:
            #     logger.debug(f"Roku TV not currently supported ☹️")
            self.found_users_sessions = False
            # self.active_session = None
            self.can_seek = False
        elif len(user_sessions) > 1:
            logger.error(f"More than one session found for {self.user}")
            self.found_users_sessions = False
            # self.active_session = None
            self.can_seek = False
        else:
            sess = user_sessions[0]
            self.found_users_sessions = True
            # self.active_session = sess
            self.can_seek = True
        # logger.debug(f"Active Session: {self.active_session}")

    def get_playing_status_from_jellyfin(self):
        if self.has_active_session() is None:
            logger.error(f"No active session found.")
            return None

        if "NowPlayingItem" in self.active_session.keys():
            self.media_item = self.active_session["NowPlayingItem"]
            self.position = (
                int(self.active_session["PlayState"]["PositionTicks"]) / 10_000_000
            )
            self.play_status = (
                "paused"
                if self.active_session["PlayState"]["IsPaused"] == True
                else "playing"
            )
        else:
            self.media_item = None
            self.position = 0
            self.play_status = "stopped"
        return self.status_dict()

        user: str = field(init=False)
        url: str = field(init=False)
        password: str = field(init=False)

        is_connected: bool = False
        active_session: defaultdict[dict] = field(
            default_factory=lambda: defaultdict(dict)
        )
        can_seek: bool = False
        found_users_sessions: bool = False

    def status_dict(self):
        if self.media_item is None:
            return {
                "jf_id": None,
                "title": None,
                "path": None,
                "status": "stopped",
                "position": 0,
                "is_connected": self.is_connected,
                "active_session": self.active_session,
                "session_id": self.session_id,
            }

        return {
            "jf_id": self.media_item["Id"],
            "title": self.media_item["Name"],
            "path": self.media_item["Path"],
            "status": self.play_status,
            "position": self.position,
            "is_connected": self.is_connected,
            "active_session": self.active_session,
            "session_id": self.session_id,
        }

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
    try:
        jf = MyJellyfinClient()
        jf.connect()
        logger.debug("Finished connecting to Jellyfin")

        logger.debug(f"is Connected to server: {jf.is_connected}")
        logger.debug(f"Found user sessions: {jf.found_users_sessions}")
        logger.debug(f"Has Active Session: {jf.has_active_session()}")
    except Exception as e:
        logger.error(f"Error: {e}")
