import pytest

from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_playlist_items,
    get_user_favorites,
    get_user_playlists,
    refresh_library,
)


@pytest.mark.skip(reason="Need to have a Jellyfin server running")
def test_can_ping_server():
    assert can_ping_server() is True


@pytest.mark.skip(reason="Need to have a Jellyfin server running")
def test_refresh_library():
    assert refresh_library().status_code == 204


@pytest.mark.skip(reason="Need to have a Jellyfin server running")
def test_get_user_favorites():
    assert get_user_favorites() is not None


@pytest.mark.skip(reason="Need to have a Jellyfin server running")
def test_playlists():
    playlists = get_user_playlists()
    assert len(playlists) > 0
    p = playlists[0]
    items = get_playlist_items(p["Id"])
    assert len(items) > 0
