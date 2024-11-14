import json
import re
from urllib.parse import quote

import requests
from loguru import logger
from jellyfin_apiclient_python import JellyfinClient

# for the 3rd time im restarting the jellyfin functions
# keeping the my_jellyfin_client for existing code
# try to use this for future
from hmtc.config import init_config

config = init_config()

user = config["jellyfin"]["user"]
user_jf_id = config["jellyfin"]["user_id"]
base_url = config["jellyfin"]["url"]
client = JellyfinClient()


def jf_user_request(method, _url, params=None, data=None):
    # started working on this to get playlists from jellyfin
    # didn't get it working 11/13/24
    client.config.app("hmtc-user", "0.0.1", "my machine jf_requests", "some other id")
    client.config.data["auth.ssl"] = True
    client.config.data["auth.username"] = config["jellyfin"]["user"]
    client.config.data["auth.password"] = config["jellyfin"]["password"]
    client.auth.connect_to_address(config["jellyfin"]["url"])
    client.auth.login(
        config["jellyfin"]["url"],
        config["jellyfin"]["user"],
        config["jellyfin"]["password"],
    )

    credentials = client.auth.credentials.get_credentials()
    server = credentials["Servers"][0]

    server["username"] = config["jellyfin"]["user"]

    dumped_server = json.dumps(server)

    client.authenticate({"Servers": [server]}, discover=False)
    logger.debug(f"Some log message")
    response = client.http.request_url(dict(url=_url, params=params, data=data))
    logger.debug(f"Response: {response}")


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


def jf_post(url, data=None):
    return jf_request("POST", url, data=data)


def get_jellyfin_playlist_items(playlist_id):
    # doesn't work as of 10/25/2024
    url = f"/Playlists/{playlist_id}/Users"
    try:
        res = jf_get(url=url)
    except Exception as e:
        return {"error": str(e)}
    if res.status_code != 200:
        # when does this happen?
        logger.error(f"Error getting playlist items: {res.status_code}")
        return res
    return res.json()


def create_jellyfin_playlist(title="New Playlist"):
    # doesn't work as of 10/25/2024
    url = "/Playlists"

    payload = {
        "Name": str(title),
        "UserId": user_jf_id,
        "MediaType": "Music",
    }
    res = jf_post(url=url, data=payload)
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
    # started working on this to get playlists from jellyfin
    # didn't get it working 11/13/24
    url = f"/Playlists/{playlist_id}/Items"
    res = jf_user_get(url=url)
    if res is None:
        logger.error(f"Error getting playlist items: response is None")
        return None
    if res.status_code != 200:
        logger.error(f"Error getting playlist items: {res.status_code}")
        return None

    items = [x for x in res.json()["Items"]]
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
    favs = get_user_favorites()
    print([x["Name"] for x in favs])
    refresh_library()
    print(len(favs))
    print(f"videos {sources_library_id()}")
    print(f"tracks {tracks_library_id()}")
    # x = search_for_media(library="track", title="pineapple, birthday, city")
    print(get_user_id("mizzle"))
    jf_playpause()
