import time

import ipyvuetify as v
import solara
import solara.lab


def test_docs_no_browser_api_find():
    clicks = solara.reactive(0)

    @solara.component
    def ClickButton():
        def increment():
            clicks.value += 1

        with solara.Card("Button in a card"):
            with solara.Column().meta(ref="my_column"):
                solara.Button(label=f"Clicked: {clicks}", on_click=increment)
            with solara.Column():
                solara.Button(label="Not the button we need")

    # rc is short for render context
    box, rc = solara.render(ClickButton(), handle_error=False)
    # this find will make the .widget fail, because it matches two buttons
    # finder = rc.find(v.Btn)
    # We can refine our search by adding constraints to attributes of the widget
    button_locator = rc.find(v.Btn, children=["Clicked: 0"])
    # basics asserts are supported, like assert_single(), assert_empty(), assert_not_empty()
    button_locator.assert_single()
    button = button_locator.widget
    # .find calls can also be nested, and can use the meta_ref to find the right widget
    # finder = rc.find(meta_ref="my_column").find(v.Btn)
    button.click()
    assert clicks.value == 1
    rc.find(v.Btn, children=["Clicked: 1"]).assert_single()


def test_docs_no_browser_api_thread():
    clicks = solara.reactive(0)

    @solara.component
    def ClickButton():
        @solara.lab.task
        def increment():
            # now we will wait for 0.3 seconds before updating the UI
            time.sleep(0.3)
            clicks.value += 1

        with solara.Card("Button in a card"):
            with solara.Column():
                solara.Button(label=f"Clicked: {clicks}", on_click=increment)

    # rc is short for render context
    box, rc = solara.render(ClickButton(), handle_error=False)
    finder = rc.find(v.Btn)
    button = finder.widget
    finder.assert_single()
    finder.assert_not_empty()
    assert button.children[0] == "Clicked: 0"

    # clicking will now start a thread, so we have to wait/poll for the UI to update
    button.click()

    button_after_delayed_click = rc.find(v.Btn, children=["Clicked: 1"])
    button_after_delayed_click.wait_for(timeout=2.5)
