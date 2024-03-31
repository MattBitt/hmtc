from textual.app import App


from hmtc.ui.screens import (
    DashboardScreen,
    QuitScreen,
    SettingsScreen,
    HelpScreen,
    PlaylistListScreen,
)


class HMTCApp(App):
    CSS_PATH = "tui.tcss"
    TITLE = "Harry Mack Track Creator"
    SUB_TITLE = "All HMack, all the time."
    BINDINGS = [
        ("d", "switch_mode('dashboard')", "Dashboard"),
        ("p", "switch_mode('playlist_list')", "Playlists"),
        ("s", "switch_mode('settings')", "Settings"),
        ("h", "switch_mode('help')", "Help"),
        ("q", "request_quit", "Quit"),
        ("escape", "request_quit"),
    ]

    MODES = {
        "dashboard": DashboardScreen,
        "settings": SettingsScreen,
        "playlist_list": PlaylistListScreen,
        "help": HelpScreen,
    }

    def on_mount(self) -> None:
        self.switch_mode("playlist_list")

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.push_screen(QuitScreen())
