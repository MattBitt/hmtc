from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    create_jellyfin_playlist,
    get_jellyfin_playlist_items,
    get_user_favorites,
    get_user_session,
    refresh_library,
)


def test_can_ping_server():
    assert can_ping_server() is True


def test_refresh_library():
    assert refresh_library().status_code == 204


def test_get_user_favorites():
    assert get_user_favorites() is not None
