from typing import Callable

import solara

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.transitions.swap import SwapTransition
from hmtc.domains.base_domain import BaseDomain

@solara.component
def Result(status, message):
    if status == "warning":
        solara.Warning(f"{message}")

    elif status == "success":
        solara.Success(f"{message}")
    else:
        solara.Error(f"{status} {message}")

@solara.component
def FunctionButton(
    item: BaseDomain,
    label: str,
    icon: str,
    some_function: Callable,

):
    performed = solara.use_reactive(False)
    result = solara.use_reactive(None)

    def perform():
        _result = some_function(item)
        performed.set(True)
        
        if _result is True:
            result.set("success")
        else:
            result.set("warning")


    with SwapTransition(show_first=(performed.value == False), name="fade"):
        solara.Button(
            f"{label}", classes=["button"], on_click=perform, icon_name=icon
        )
        Result(result.value, label)


