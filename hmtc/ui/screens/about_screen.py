from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class AboutScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("About Screen")
        yield Footer()
