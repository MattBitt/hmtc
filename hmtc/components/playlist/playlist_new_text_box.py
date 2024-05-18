from typing import Callable

import reacton.ipyvuetify as v
import solara

from hmtc.schemas.playlist import PlaylistItem


@solara.component
def PlaylistNewTextBox(on_new: Callable[[PlaylistItem], None]):
    """Component that managed entering new playlist items"""
    new_text, set_new_text = solara.use_state("")
    text_field = v.TextField(
        v_model=new_text, on_v_model=set_new_text, label="Enter a new playlist item"
    )

    def create_new_item(*ignore_args):
        if not new_text:
            return
        new_item = PlaylistItem(title=new_text, enabled=False)
        on_new(new_item)
        # reset text
        set_new_text("")

    v.use_event(text_field, "keydown.enter", create_new_item)
    return text_field
