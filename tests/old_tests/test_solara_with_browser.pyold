import ipywidgets as widgets
import playwright.sync_api
from IPython.display import display


# this doesn't really seem to work.....
# i change the text and the test keeps passing...
def test_widget_button_solara(solara_test, page_session: playwright.sync_api.Page):
    # The test code runs in the same process as solara-server (which runs in a separate thread)
    # Note: this test uses ipywidgets directly, not solara components.
    button = widgets.Button(description="Click Me!22")

    def change_description(obj):
        button.description = "Tested event2"

    button.on_click(change_description)
    display(button)
    button_sel = page_session.locator("text=Click Me!")
    button_sel.wait_for()
    button_sel.click()
    page_session.locator("text=Tested event").wait_for()
