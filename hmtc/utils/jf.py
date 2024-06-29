from jellyfin_apiclient_python import JellyfinClient
import json
from uuid import uuid1
from hmtc.config import init_config

config = init_config()

url = config["jellyfin"]["url"]
user = config["jellyfin"]["user"]
password = config["jellyfin"]["password"]


client = JellyfinClient()

client.config.app("your_brilliant_app", "0.0.1", "machine_name", uuid1())
client.config.data["auth.ssl"] = True

client.auth.connect_to_address(url)
client.auth.login(url, user, password)


def grab_session():

    credentials = client.auth.credentials.get_credentials()
    server = credentials["Servers"][0]
    server["username"] = "matt"

    client.authenticate(credentials, discover=False)
    status = "stopped"
    if client.logged_in:
        for sess in client.jellyfin.sessions():
            if sess["UserName"] == "firefox":
                return sess

    else:
        print("login failed")


def grab_now_playing():

    session = grab_session()
    if session is None:
        print("No session found")
    else:
        position = int(session["PlayState"]["PositionTicks"]) / 10_000_000
        status = "paused" if session["PlayState"]["IsPaused"] is True else "playing"
        now_playing = session["NowPlayingItem"]
        print(f"Current status: {status}")
        print(f"Current position: {position}")

        return (
            {
                "title": now_playing["Name"],
                "path": now_playing["Path"],
                "status": status,
                "position": position,
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


def play_client():
    session = grab_session()
    if session is None:
        print("No session found")
    else:
        client.jellyfin.remote_playpause(session["Id"])


def seek_forward(milliseconds):
    session = grab_session()
    if session is None:
        print("No session found")
    else:
        client.jellyfin.remote_seek(session["Id"], milliseconds)


# print(grab_now_playing())
