import solara


@solara.component
def AppBar():

    with solara.AppBar():

        icon_name = "mdi-account-cog"

        button_text = "Account Settings"
        solara.Button(button_text, icon_name=icon_name, color="blue")
        solara.Title(f"HMTC")
