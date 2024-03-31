from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class PlaylistEditScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("PlaylistEdit Screen")
        yield Footer()
