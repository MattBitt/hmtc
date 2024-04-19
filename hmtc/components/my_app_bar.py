import solara


@solara.component
def MyAppBar():

    with solara.AppBarTitle():

        icon_name = "mdi-account-cog"
        button_text = ""
        solara.Button(button_text, icon_name=icon_name)
        solara.Title("HMTC")
