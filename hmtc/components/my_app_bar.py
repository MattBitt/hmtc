import solara


@solara.component
def MyAppBar(title="HMTC", env=None):
    icon_name = "mdi-account-cog"
    button_text = "Settings"
    if env is None:
        color = "black"
    elif env == "development":
        color = "blue"
    elif env == "testing":
        color = "green"
    elif env == "production":
        color = "red"
    else:
        color = "purple"

    with solara.AppBarTitle():

        with solara.Row():
            solara.Title("HMTC")
            solara.Markdown("asdfqwerasdf")
            solara.Button(button_text, icon_name=icon_name, style={"color": color})
