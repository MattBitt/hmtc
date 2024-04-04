from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Label, Header
from textual.widgets import Static
from textual.containers import Container, Horizontal, VerticalScroll
from hmtc.db import get_list_videos
from textual.widgets import ListItem, ListView

TEXT = """\
Docking a widget removes it from the layout and fixes its position, aligned to either the top, right, bottom, or left edges of a container.

Docked widgets will not scroll out of view, making them ideal for sticky headers, footers, and sidebars.

"""


class PlaylistListScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with VerticalScroll(id="left-pane"):
                yield Label("You Tube Playlists", id="playlistlabel")
                pls = get_list_videos()
                x = [ListItem(Label(p)) for p in pls]
                yield ListView(*x, classes="playlistlist")

            with Horizontal(id="top-right"):
                yield Static("Horizontally")
                yield Static("Positioned")
                yield Static("Children")
                yield Static("Here")
            with Container(id="bottom-right"):
                yield Static("This")
                yield Static("panel")
                yield Static("is")
                yield Static("using")
                yield Static("grid layout!", id="bottom-right-final")
        yield Footer()

    def on_mount(self) -> None:
        pass
