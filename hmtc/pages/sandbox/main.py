import solara
import solara.lab
from loguru import logger

from hmtc.components.shared import Chip, InputAndDisplay, MySpinner

open_delete_confirmation = solara.reactive(False)


def delete_user():
    # put your code to perform the action here
    print("User being deleted...")


@solara.component
def Sandbox():
    solara.Button(
        label="Delete user", on_click=lambda: open_delete_confirmation.set(True)
    )
    solara.lab.ConfirmationDialog(
        open_delete_confirmation,
        ok="Ok, Delete",
        on_ok=delete_user,
        content="Are you sure you want to delete this user?",
    )
    with solara.Columns():
        MySpinner()
        Chip(item="first chip", event_close=lambda: logger.debug("removing"))
        Chip(item="second chip")
