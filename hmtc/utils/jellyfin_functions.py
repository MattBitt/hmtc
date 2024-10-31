import json
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
    session = [
        x for x in all_sessions() if (x["UserName"] == user and x["Client"] != "hmtc")
    ]
    if len(session) == 0:
        return None
    elif len(session) > 1:
        # logger.error("More than one session found")
        return session[0]
    else:
        return session[0]


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
        return None
    if "NowPlayingItem" not in session.keys():
        return None
    return session["NowPlayingItem"]["Id"]


def get_user_libraries():
    url = f"/Users/{user_jf_id}/Items"
    try:
        res = jf_get(url=url)
    except Exception as e:
        return None
    libraries = [x for x in res.json()["Items"]]
    return libraries


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


import re


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
    x = search_for_media(library="track", title="pineapple, birthday, city")
    print(get_user_id("mizzle"))
