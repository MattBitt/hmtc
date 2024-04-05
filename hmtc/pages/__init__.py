import solara
from hmtc.main import setup
from pathlib import Path

db = setup()


app_state = solara.reactive(0)
solara.Style(Path("hmtc/assets/style.css"))
