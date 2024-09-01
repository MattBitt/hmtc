import time
from jellyfin_apiclient_python import JellyfinClient
from uuid import uuid1
from hmtc.config import init_config
from hmtc.utils.my_logging import logger

# from enum import Enum, IntEnum
from aenum import Enum

config = init_config()

url = config["jellyfin"]["url"]
user = config["jellyfin"]["user"]
password = config["jellyfin"]["password"]


client = JellyfinClient()

client.config.app("hmtc", "0.0.a", "this_machine", "this_version")
client.config.data["auth.ssl"] = True

client.auth.connect_to_address(url)
client.auth.login(url, user, password)


def grab_sessions():

    credentials = client.auth.credentials.get_credentials()
    # need to check for empty credentials
    s = credentials["Servers"]
    # logger.debug(f"Found {len(s)} Jellyfin Servers")
    if s == []:
        logger.error("No Jellyfin Servers found")
        return None

    # not sure what this does 8-30-24
    server = credentials["Servers"][0]
    server["username"] = "matt"

    client.authenticate(credentials, discover=False)

    if client.logged_in:
        sessions_list = []

        total_sessions = len(client.jellyfin.sessions())

        for sess in client.jellyfin.sessions():
            if sess["UserName"] == user and sess["Client"] != "hmtc":

                if sess["SupportsMediaControl"] is True:
                    sessions_list.append(sess)
                else:

                    logger.debug(
                        f"This session doesn't support media control: {sess['Client']}"
                    )
        logger.debug(
            f"Current sessions: {len(sessions_list)} of {total_sessions} total"
        )

        return sessions_list
    else:
        print("login failed")
        logger.error("Error Connecting to Jellyfin")
        return None


def grab_now_playing(session=None):

    if session["PlayState"]["CanSeek"] is False:
        logger.error("Cannot seek")
        now_playing = None
    else:
        position = int(session["PlayState"]["PositionTicks"]) / 10_000_000
        status = "paused" if session["PlayState"]["IsPaused"] is True else "playing"
        now_playing = session["NowPlayingItem"]
        path_str = session["NowPlayingItem"]["Path"]
        if "inputs" in path_str:
            item_type = "input"
        else:
            item_type = "track"
        try:
            item = session["NowPlayingQueueFullItems"][0]
        except:
            logger.debug("No item found in NowPlayingQueueFullItems")
            return None

        # logger.debug(f"Current status: {status}")
        # logger.debug(f"Current position: {position}")

    return (
        {
            "jf_id": now_playing["Id"],
            "title": now_playing["Name"],
            "path": now_playing["Path"],
            "status": status,
            "position": position,
            "tags": item["Tags"],
            "type": item_type,
        }
        if now_playing
        else None
    )


# jellyfin command examples
# client.jellyfin.remote_pause(session["Id"])
# client.jellyfin.remote_playpause(session["Id"])
# body = client.jellyfin.get_items([item["jf_id"]])["Items"][0]
# body["Tags"] = tags
# # POST with the new information
# handler = "Items/" + body["Id"]
# client.jellyfin._post(handler, params=None, json=body)
# client.jellyfin.post_session(
# session["Id"],
# "Playing",
# {"PlayCommand": "PlayNow", "ItemIds": jellyfin_id, "StartPositionTicks": 10000},
# )
#         # ob1 jellyfin id: cdb49ff3e5ab6df7980078bd2562f67d
#


def jellyfin_playpause():
    # this only works if there is only one session
    session = grab_sessions()[0]

    logger.debug(f"Supports Media Control? {session['SupportsMediaControl']}")
    logger.debug(f"Supports Remote Control? {session['SupportsRemoteControl']}")
    client.jellyfin.remote_playpause(session["Id"])


def jellyfin_sessions():
    # if not client.logged_in:
    #     logger.error("No jellyfin server found")
    #     return None
    all_sessions = grab_sessions()
    return [sess for sess in all_sessions]


def jellyfin_connection_test():
    try:
        client.jellyfin.get_system_info()
        logger.debug("Jellyfin connection test successful")

        return True
    except Exception as e:
        logger.error(f"Error connecting to Jellyfin {e}")
        return False


def jellyfin_seekto(position):
    session = grab_sessions()[0]
    client.jellyfin.remote_pause(session["Id"])
    client.jellyfin.remote_seek(session["Id"], position * 10_000_000)
    client.jellyfin.remote_playpause(session["Id"])


def jellyfin_loop_2sec(position):
    # maybe this should be a task?
    session = grab_sessions()[0]
    client.jellyfin.remote_pause(session["Id"])
    client.jellyfin.remote_seek(session["Id"], position * 10_000_000)
    client.jellyfin.remote_playpause(session["Id"])
    time.sleep(2)
    client.jellyfin.remote_pause(session["Id"])
    client.jellyfin.remote_seek(session["Id"], position * 10_000_000)
