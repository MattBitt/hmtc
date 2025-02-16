import json
import re
import time
from urllib.parse import quote

import requests
from loguru import logger

from hmtc.config import init_config

config = init_config()

user = config["jellyfin"]["user"]
user_jf_id = config["jellyfin"]["user_id"]
base_url = config["jellyfin"]["url"]
client = config["jellyfin"]["client"]
device = config["jellyfin"]["device"]
device_id = config["jellyfin"]["device_id"]
access_token = ""


def generate_auth_string():

    auth_string = f'Emby UserId="{user}", Client="{client}", Device="{device}", DeviceId="{device_id}", Version="0.1", Token="{access_token}"'
    return auth_string.format(
        user=user,
        client=client,
        device=device,
        device_id=device_id,
        access_token=access_token,
    )


def jf_user_request(method, _url, params=None, data=None):
    global access_token
    if access_token == "":
        access_token = login()
        if access_token is None:
            raise Exception("Error logging in to Jellyfin")

    auth = generate_auth_string()
    headers = {
        "X-Emby-Authorization": auth,
        "Content-Type": "application/json",
    }
    url = base_url + _url
    resp = requests.request(method, url=url, params=params, data=data, headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        return data
    elif resp.status_code == 204:
        return 204
    else:
        print("An error occurred while attempting to retrieve data from the API.")
        logger.error(resp.json())
        return None


def get_auth_key(username, password):
    # Get Auth Token for admin account
    values = {"Username": username, "Pw": password}
    DATA = json.dumps(values)
    DATA = DATA.encode("utf-8")
    DATA = bytes(DATA)

    headers = {
        "X-Emby-Authorization": generate_auth_string(),
        "Content-Type": "application/json",
    }

    url = config["jellyfin"]["url"] + "/Users/AuthenticateByName"

    response = requests.post(url, headers=headers, data=DATA)
    if response.status_code == 200:
        data = response.json()
        return data["AccessToken"]
    else:
        logger.error(
            "An error occurred while attempting to retrieve data from the API."
        )


def login():
    return get_auth_key(
        username=config["jellyfin"]["user"],
        password=config["jellyfin"]["password"],
    )


def jf_request(method, _url, params=None, data=None):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-mediabrowser-token": config["jellyfin"]["api"],
    }
    url = base_url + _url
    return requests.request(method, url=url, params=params, data=data, headers=headers)


def jf_get(url, params=None):
    return jf_request("GET", url, params=params)


def jf_user_get(url, params=None):
    return jf_user_request("GET", url, params=params)


def jf_user_post(url, data=None):
    # untested as of 11/14/24
    return jf_user_request("POST", url, data=data)


def jf_post(url, data=None):
    return jf_request("POST", url, data=data)


def create_jellyfin_playlist(title="New Playlist"):
    # doesn't work as of 10/25/2024
    url = "/Playlists"
    favs = get_user_favorites()
    fav_ids = [x["Id"] for x in favs]
    payload = {
        "Name": str(title),
        "UserId": user_jf_id,
        "MediaType": "Music",
        "Ids": fav_ids,
        "Users": [{"UserId": user_jf_id, "CanEdit": True}],
        "IsPublic": True,
    }
    res = jf_user_post(url=url, data=payload)
    return res


def get_user_favorites():
    url = f"/Users/{user_jf_id}/Items?Recursive=True&Filters=IsFavorite"
    try:
        resp = json.loads(jf_get(url=url).content)["Items"]
    except Exception as e:
        return None

    return resp


def can_ping_server():
    try:
        res = jf_get("/Users")
        return res.status_code == 200
    except Exception as e:
        return False


def get_list_of_users():
    url = f"/Users"
    res = jf_get(url=url)
    if res.status_code != 200:
        logger.error(f"Error getting users {res}")
        return None
    resp_dict = res.json()

    items = [(x["Name"], x["Id"]) for x in resp_dict]
    return items


def all_sessions():
    try:
        res = jf_get("/Sessions")
        return res.json()
    except Exception as e:
        logger.error(e)
        return None


def get_user_session():
    x = all_sessions()
    if x is None:
        logger.error("No jellyfin sessions found")
        return None
    if len(x) == 0:
        logger.debug(f"all_sessions: returned 0")
        return None

    session = [
        x
        for x in all_sessions()
        if ("hmtc" not in x["Client"] and x.get("UserName", "") == user)
    ]
    if len(session) == 0:
        # logger.error("No sessions found")
        return {
            "Id": "",
            "PlayState": {"PositionTicks": 0},
            "NowPlayingItem": {"Id": 0, "Name": "", "RunTimeTicks": 0},
            "UserName": user,
            "DeviceName": "no-device",
        }
    else:
        if len(session) > 1:
            _sess = session[0]
            last_activity = _sess["LastActivityDate"]
            for sess in session[1:]:
                if sess["LastActivityDate"] > last_activity:
                    _sess = sess
                    last_activity = sess["LastActivityDate"]
        else:
            _sess = session[0]

        # logger.error(
        #     f"More than one session found for user {user}: {[s['Client'] for s in session]}. Using the most recent one {_sess['Client']}"
        # )
        if "PositionTicks" not in _sess["PlayState"].keys():
            _sess["PlayState"]["PositionTicks"] = 0
        if "NowPlayingItem" not in _sess.keys():
            _sess["NowPlayingItem"] = {
                "Id": 0,
                "Name": "no-name",
                "RunTimeTicks": 0,
            }
        return _sess


def get_current_user_timestamp():
    session = get_user_session()
    if session is None:
        return None
    if "NowPlayingItem" not in session.keys():
        return None
    return session["PlayState"]["PositionTicks"] / 10000000


def get_currently_playing():
    session = get_user_session()
    if session is None:
        return ""
    if "NowPlayingItem" not in session.keys():
        return ""
    if session["NowPlayingItem"]["Id"] == 0:
        return ""
    return session["NowPlayingItem"]["Id"]


def get_user_libraries():
    url = f"/Users/{user_jf_id}/Items"
    try:
        res = jf_get(url=url)
    except Exception as e:
        raise e
    if res.status_code != 200:
        logger.error(f"Error gettings user libraries {res}")
        return []
    resp_dict = res.json()
    libraries = [x for x in resp_dict["Items"]]
    return libraries


def get_user_playlists():
    url = f"/Users/{user_jf_id}/Items?Recursive=true&Filters=IsFolder&IncludeItemTypes=Playlist"
    try:
        res = jf_get(url=url)
    except Exception as e:
        logger.error(f"Error getting user playlists: {e}")
        return None
    playlists = [x for x in res.json()["Items"]]
    return playlists


def get_playlist_items(playlist_id):
    url = f"/Playlists/{playlist_id}/Items"
    res = jf_user_get(url=url)
    if res is None:
        logger.error(f"Error getting playlist items: response is None")
        return None
    items = [x for x in res["Items"]]
    return items


def sources_library_id():
    libraries = get_user_libraries()
    source = config["jellyfin"]["sources_library"]
    for lib in libraries:
        if lib["Name"] == source:
            return lib["Id"]
    return None


def tracks_library_id():
    libraries = get_user_libraries()
    for lib in libraries:
        if lib["Name"] == "HarryMackTracks":
            return lib["Id"]
    return None


def search_for_media(library, title):
    if library == "videos":
        logger.debug(f"searching for sources library {library} {title}")
        library_id = sources_library_id()
    else:
        logger.debug(f"searching for tracks library {library} {title}")
        library_id = tracks_library_id()

    if library_id is None:
        logger.error(f"{library} library not found")
        return None

    url = f"/Users/{user_jf_id}/Items?Recursive=true&ParentId={library_id}&SearchTerm={title}"
    res = jf_get(url)

    if res.status_code != 200:
        logger.error(f"Error searching for media: {res.status_code}")
        return None

    resp_dict = res.json()

    if resp_dict["TotalRecordCount"] == 0:
        logger.error(f"No results for {title}")
        return None
    else:
        items = [item for item in resp_dict["Items"] if not item["IsFolder"]]
        if items == []:
            logger.error(f"No non-folder results for {title}")
            return None
        if len(items) > 1:
            logger.error(f"{len(items)} folder results for {title}")
            return None

        return items[0]


def jf_playpause():
    session = get_user_session()
    url = f"/Sessions/{session['Id']}/Playing/PlayPause"
    res = jf_post(url)
    return res


def jf_play():
    session = get_user_session()
    url = f"/Sessions/{session['Id']}/Playing/Play"
    res = jf_post(url)
    return res


def jf_pause():
    session = get_user_session()
    url = f"/Sessions/{session['Id']}/Playing/Pause"
    res = jf_post(url)
    return res


def jf_stop():
    session = get_user_session()
    url = f"/Sessions/{session['Id']}/Playing/Stop"
    res = jf_post(url)
    return res


def jf_seek_to(position):
    session = get_user_session()
    video_id = get_currently_playing()
    url = f"/Sessions/{session['Id']}/Playing/Seek?seekPositionTicks={position}"

    res = jf_user_post(url)
    return res


def refresh_library():
    url = f"/Library/Refresh"
    res = jf_post(url)
    return res


def get_user_id(user_name):
    # use this to get the user id for the user_name
    url = f"/Users/Public"
    res = jf_get(url)
    if res.status_code != 200:
        logger.error(f"Error getting user ids: {res.status_code}")
        return None
    if res.json() == []:
        logger.error(f"Error getting user id: {user_name} not found")
        return None
    for item in res.json():
        if item["Name"] == user_name:
            return item["Id"]


def load_media_item(media_id):
    session = get_user_session()
    url = f"/Sessions/{session['Id']}/Playing?playCommand=PlayNow&itemIds={media_id}"
    res = jf_post(url)
    if res.status_code != 204:
        logger.error(f"Error loading media item {res}")
        return None
    logger.success(f"Loading media_id {media_id} succeeded")


if __name__ == "__main__":

    media = search_for_media("videos", "lZutXgamSZI")
    load_media_item(media["Id"])
