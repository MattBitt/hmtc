import solara

@solara.component
def MyButton(label, on_click, icon_name="", color="primary", **kwargs):
    
    def clicked(*item):
        on_click(item)
    
    color_class = ['button'] + ([color] if color != 'primary' else [])
    
    
    solara.Button(label=label, on_click=clicked, icon_name=icon_name, classes=color_class, **kwargs )