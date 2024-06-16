import solara


def SearchableTextbox(label, input_text, continuous_update=False):
    with solara.Column():
        with solara.Row():
            solara.InputText(
                label,
                value=input_text,
                continuous_update=continuous_update,
            )
