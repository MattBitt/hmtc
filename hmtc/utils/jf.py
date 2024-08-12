from jellyfin_apiclient_python import JellyfinClient
import json
from uuid import uuid1
from hmtc.config import init_config
from hmtc.utils.my_logging import logger

# from enum import Enum, IntEnum
from aenum import Enum

config = init_config()

url = config["jellyfin"]["url"]
user = config["jellyfin"]["user"]
password = config["jellyfin"]["password"]


class RATINGS(Enum):

    STAR1 = 1
    STAR2 = 2
    STAR3 = 3
    STAR4 = 4
    STAR5 = 5


client = JellyfinClient()

client.config.app("hmtc", "0.0.a", "this_machine", uuid1())
client.config.data["auth.ssl"] = True

client.auth.connect_to_address(url)
client.auth.login(url, user, password)


def grab_session():

    credentials = client.auth.credentials.get_credentials()
    # need to check for empty credentials
    s = credentials["Servers"]
    if s == []:
        logger.error("No Jellyfin Servers found")
        return None

    server = credentials["Servers"][0]
    server["username"] = "matt"

    client.authenticate(credentials, discover=False)
    if client.logged_in:
        for sess in client.jellyfin.sessions():
            if sess["UserName"] == "firefox":
                return sess

    else:
        print("login failed")
        return None


def grab_now_playing():

    session = grab_session()
    if session is None:
        print("No session found")
    else:
        if session["PlayState"]["CanSeek"] is False:
            print("Cannot seek")
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

            item = session["NowPlayingQueueFullItems"][0]

            print(f"Current status: {status}")
            print(f"Current position: {position}")

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


def pause_client():
    session = grab_session()
    if session is None:
        print("No session found")
    else:
        client.jellyfin.remote_pause(session["Id"])
    # what makes sense to return, anything?


def play_client():
    session = grab_session()
    if session is None:
        print("No session found")
    else:
        client.jellyfin.remote_playpause(session["Id"])
    # what makes sense to return, anything?


def add_tag_to_item(tag):
    if tag is None or "":
        return

    item = grab_now_playing()

    # Get all information from the API
    body = client.jellyfin.get_items([item["jf_id"]])["Items"][0]

    # Modify properties you want

    tags = [t for t in body["Tags"]]
    if tag not in tags:
        tags.append(tag)
        body["Tags"] = tags

        # POST with the new information
        handler = "Items/" + body["Id"]
        client.jellyfin._post(handler, params=None, json=body)
        return True
    else:
        logger.error(f"Tag {tag} already exists on item {item['jf_id']}")
        return False


if __name__ == "__main__":
    item = grab_now_playing()
    add_tag_to_item(item["id"], "star:5")
