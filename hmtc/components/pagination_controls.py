from typing import Callable

import solara
from hmtc.assets.colors import Colors


@solara.component
def PaginationControls(
    current_page: solara.Reactive[int],
    num_pages: solara.Reactive[int],
    on_page_change: Callable[[], None],
):
    is_first = current_page.value == 1
    is_last = current_page.value == num_pages.value

    def set_page(page):
        if page < 1:
            page = 1
        if page > num_pages.value:
            page = num_pages.value
        on_page_change(page)

    with solara.Row():
        solara.Button(
            "First",
            on_click=lambda: set_page(1),
            disabled=is_first,
        )
        solara.Button(
            "Previous",
            on_click=lambda: set_page(current_page.value - 1),
            disabled=(current_page.value == 1),
        ),

        solara.Button(
            "Next",
            on_click=lambda: set_page(current_page.value + 1),
            disabled=(current_page.value == num_pages.value),
        )
        solara.Button(
            "Last",
            on_click=lambda: set_page(num_pages.value),
            disabled=is_last,
        )
        # SingleSelect("Videos per page", per_page, [5, 10, 20, 50, 100])
        solara.Markdown(f"Page {current_page.value} of {num_pages.value}")
