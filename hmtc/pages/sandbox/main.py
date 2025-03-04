from typing import List

# from hmtc.components.shared import Chip, InputAndDisplay, MySpinner
# from hmtc.components.video.jf_panel import JFPanel
# from hmtc.domains.video import Video
# from hmtc.models import Video as VideoModel
# @solara.component
# def Sandbox():
#     vid = VideoModel.select().where(VideoModel.unique_content == True).first()
#     video = Video(vid.id)
#     JFPanel(video)
#     solara.Markdown(f"Sandbox Page.")
import solara

# import solara.lab
from loguru import logger


# Mock superchat data (would be replaced with real data from the database)
class Superchat:
    def __init__(self, id: int, image_url: str, timestamp: str):
        self.id = id
        self.image_url = image_url
        self.timestamp = timestamp


# Example dataset
superchats = [
    Superchat(i, f"https://placehold.co/150x100?text={i}", f"00:{i:02d}")
    for i in range(1, 101)
]

# State management
selected_superchats = solara.reactive(set())
current_page = solara.reactive(0)
items_per_page = 12


def toggle_selection(superchat_id: int):
    if superchat_id in selected_superchats.value:
        selected_superchats.value.remove(superchat_id)
    else:
        selected_superchats.value.add(superchat_id)
    selected_superchats.set(selected_superchats.value)


def merge_selected():
    if selected_superchats.value:
        print(f"Merging superchats: {sorted(selected_superchats.value)}")
        selected_superchats.set(set())


def paginate(direction: int):
    new_page = current_page.value + direction
    if 0 <= new_page < (len(superchats) // items_per_page) + 1:
        current_page.set(new_page)


# def Sandbox():SuperchatGrid
@solara.component
def Sandbox():
    start = current_page.value * items_per_page
    end = start + items_per_page
    displayed_superchats = superchats[start:end]

    with solara.Column():
        with solara.GridFixed(columns=4):
            for chat in displayed_superchats:
                selected = chat.id in selected_superchats.value
                with solara.Card():
                    with solara.Row():
                        solara.Image(chat.image_url, width="150")
                        solara.Text(chat.timestamp)
                        solara.Button(
                            icon_name="mdi-account",
                            on_click=lambda c=chat: toggle_selection(c.id),
                            classes=["button"],
                        )

        with solara.Row():
            solara.Button(
                "Previous",
                on_click=lambda: paginate(-1),
                disabled=current_page.value == 0,
            )
            solara.Button(
                "Next", on_click=lambda: paginate(1), disabled=end >= len(superchats)
            )

        solara.Button(
            "Merge Selected",
            on_click=merge_selected,
            disabled=len(selected_superchats.value) < 2,
        )
