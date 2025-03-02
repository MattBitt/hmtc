from typing import Callable

import solara

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.transitions.swap import SwapTransition
from hmtc.domains.base_domain import BaseDomain


@solara.component
def CheckAndFix(
    item: BaseDomain,
    check_label: str,
    check_icon: str,
    check_function: Callable,
    repair_label: str,
    repair_icon: str,
    repair_function: Callable,
    repair_class:str = ""
):
    # have i performed the check for the item yet
    checked = solara.use_reactive(False)
    result_correct = solara.use_reactive(None)

    def repair():
        # after ive 'repaired' the issue, reset the state to allow
        # another check
        repair_function(item)
        checked.set(False)

    def check():
        result = check_function(item)
        checked.set(True)
        result_correct.set(result)

    with SwapTransition(show_first=(checked.value == False), name="fade"):
        solara.Button(
            f"{check_label}", classes=["button"], on_click=check, icon_name=check_icon
        )
        with SwapTransition(show_first=(result_correct.value == False)):
            solara.Button(
                f"{repair_label}",
                classes=["button", repair_class],
                on_click=repair,
                icon_name=repair_icon,
            )
            solara.Success(f"All Good!")
