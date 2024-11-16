import json
import re
from urllib.parse import quote

import requests
from loguru import logger

# for the 3rd time im restarting the jellyfin functions
# keeping the my_jellyfin_client for existing code
# try to use this for future
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
    else:
        print("An error occurred while attempting to retrieve data from the API.")
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


def all_sessions():
    try:
        res = jf_get("/Sessions")
        return res.json()
    except Exception as e:
        logger.error(e)
        return None


def get_user_session():
    x = all_sessions()

    if len(x) == 0:
        logger.debug(f"No sessions found")
        return None

    sess = None
    session = [
        x
        for x in all_sessions()
        if (x["Client"] != "hmtc-dev " and x.get("UserName", "") == user)
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
            logger.error(
                f"More than one session found: {session}. Using the most recent one"
            )
            last_activity = session[0]["LastActivityDate"]
            for s in session:
                logger.debug(f"Session Devices: {s['DeviceName']}")
                if s["LastActivityDate"] > last_activity:
                    sess = s
                    last_activity = s["LastActivityDate"]

        else:
            sess = session[0]
        if sess is None:
            logger.error("No session found")
            return None
        if "PositionTicks" not in sess["PlayState"].keys():
            sess["PlayState"]["PositionTicks"] = 0
        if "NowPlayingItem" not in sess.keys():
            sess["NowPlayingItem"] = {
                "Id": 0,
                "Name": "no-name",
                "RunTimeTicks": 0,
            }
        return sess


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
        return None
    libraries = [x for x in res.json()["Items"]]
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
    for lib in libraries:
        if lib["Name"] == "HarryMackSources":
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
        library_id = sources_library_id()
    else:
        library_id = tracks_library_id()

    url = f"/Users/{user_jf_id}/Items?Recursive=true&ParentId={library_id}&SearchTerm={title}"
    res = jf_get(url)

    if res.status_code != 200:
        logger.error(f"Error searching for media: {res.status_code}")
        return None

    elif res.json()["TotalRecordCount"] == 0:
        logger.error(f"No results for {title}")
        return None
    elif res.json()["TotalRecordCount"] > 1:
        # logger.error("More than one media found")
        logger.error(f"Too many results {title}")
        return None
    else:
        logger.debug(f"Only 1 result found! {res.json()}")
        return res.json()["Items"][0]


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
    for item in res.json():
        if item["Name"] == user_name:
            return item["Id"]


if __name__ == "__main__":
    playlists = get_user_playlists()
    if len(playlists) == 0:
        print("No playlists found")
    else:
        logger.error(f"Found {len(playlists)} playlists")
        for p in playlists:
            items = get_playlist_items(p["Id"])
            if items is None:
                logger.error(f"Error getting playlist items for {p['Name']}")
                continue
            print(f"Playlist: {p['Name']}")
            print(f"Items: {len(items)}")
    # create_jellyfin_playlist("MyFavs1114")
