from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class AppScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("App Screen")
        yield Footer()
