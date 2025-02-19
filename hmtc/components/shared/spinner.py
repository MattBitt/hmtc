import solara
from hmtc.assets.colors import Colors

@solara.component
def MySpinner():
    solara.SpinnerSolara(size="300px", color_back=Colors.ACCENT.value, color_front=Colors.PRIMARY.value)