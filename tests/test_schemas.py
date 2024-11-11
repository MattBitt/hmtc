from hmtc.schemas.channel import Channel as ChannelItem
from hmtc.schemas.playlist import PlaylistItem


def test_channel_schema():
    ChannelItem(name="asdf")


def test_playlist_schema():
    PlaylistItem(title="fdsaqwer", youtube_id="asdzzxcvdsff")
