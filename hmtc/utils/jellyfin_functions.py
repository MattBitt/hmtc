import requests

# for the 3rd time im restarting the jellyfin functions
# keeping the my_jellyfin_client for existing code
# try to use this for future
from hmtc.config import init_config
from loguru import logger
import json

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
    session = [x for x in all_sessions() if x["UserName"] == user]
    if len(session) == 0:
        return None
    elif len(session) > 1:
        logger.error("More than one session found")
        return session[0]
    else:
        return session[0]


if __name__ == "__main__":
    favs = get_user_favorites()
    print([x["Name"] for x in favs])
    print(len(favs))
