import requests

# for the 3rd time im restarting the jellyfin functions
# keeping the my_jellyfin_client for existing code
# try to use this for future
from hmtc.config import init_config

config = init_config()

user = config["jellyfin"]["user"]
user_jf_id = config["jellyfin"]["user_id"]
base_url = config["jellyfin"]["url"]

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-mediabrowser-token": config["jellyfin"]["api"],
}


def get_jellyfin_playlist_items(playlist_id):

    url = base_url + f"/Playlists/{playlist_id}/Users"

    res = requests.request("GET", url=url, headers=headers)
    if res.status_code != 200:
        return res.json()
    return res.json()


def create_jellyfin_playlist(title):
    # Create new empty playlist
    url = base_url + "/Playlists"

    payload = {
        "Name": str(title),
        "UserId": user_jf_id,
        "MediaType": "Music",
    }
    res = requests.request("POST", url=url, params=payload, headers=headers)
    return res


# resp = create_jellyfin_playlist("testing...again")
# playlist_id = resp.json()["Id"]
# print(playlist_id)
playlist_id = "625f4cece0d6ecfaa8a0ade0eee4a2e3"
print(get_jellyfin_playlist_items(playlist_id))
