import solara
from hmtc.main import setup

db = setup()


app_state = solara.reactive(0)
