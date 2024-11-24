import solara


@solara.component
def PaginationControls(current_page, num_pages, num_items):
    with solara.Row(justify="space-between"):
        solara.Button(
            "First",
            on_click=lambda: current_page.set(1),
            disabled=current_page.value == 1,
            classes=["button"],
        )
        solara.Button(
            "Previous Page",
            on_click=lambda: current_page.set(current_page.value - 1),
            disabled=current_page.value == 1,
            classes=["button"],
        )
        solara.Text(f"Current Page: {current_page.value} of {num_pages}")
        solara.Text(f"Total: {num_items}")
        solara.Button(
            "Next Page",
            on_click=lambda: current_page.set(current_page.value + 1),
            classes=["button"],
            disabled=current_page.value == num_pages,
        )
        solara.Button(
            "Last",
            on_click=lambda: current_page.set(num_pages),
            classes=["button"],
            disabled=current_page.value == num_pages,
        )
