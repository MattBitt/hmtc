from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class HelpScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Help Screen")
        yield Footer()
