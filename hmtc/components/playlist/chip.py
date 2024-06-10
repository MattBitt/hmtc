import solara


@solara.component_vue("../../components/shared/chip.vue")
def Chip(label: str, color: str = "green", icon: str = None):
    pass
