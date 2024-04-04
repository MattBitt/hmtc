from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Footer, Button, Header, RichLog
from textual import events, on
from hmtc.models import Playlist, EpisodeNumberTemplate


def get_ep_num_templates(playlist: Playlist):
    return playlist.episode_number_templates


class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:

        yield Header()
        yield Button("My First Button", id="first")
        yield RichLog()
        # query = Playlist.select().order_by(Playlist.name)
        # for playlist in query:
        #     yield Button(playlist.name, id=playlist.name[:3])

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one(RichLog).write("in on_button_pressed " + event.button.id)
        # self.app.pop_screen()

    @on(Button.Pressed)
    def log_press(self, event: Button.Pressed) -> None:
        ep_templates = (
            EpisodeNumberTemplate.select()
            .join(Playlist)
            .where(Playlist.name == "Guerilla Bars")
        )
        for template in ep_templates:
            self.query_one(RichLog).write(template.template)

    @on(events.Key)
    def log_key(self, event: events.Key) -> None:
        self.query_one(RichLog).write(event)
