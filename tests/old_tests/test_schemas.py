from hmtc.schemas.channel import Channel as ChannelItem


def test_channel_schema():
    ChannelItem(name="asdf")
