import solara
from loguru import logger


@solara.component
def SingleSelect(title, selected, all):
    with solara.Div():
        logger.debug(f"selected: {selected.value}")
        solara.ToggleButtonsSingle(selected, all)
        # solara.Markdown(f"**Selected**: {selected.value}")
