import solara


@solara.component
def PaginationControls(current_page, num_pages, num_items):
    def previous():
        if current_page.value > 1:
            current_page.set(current_page.value - 1)

    def next():
        if current_page.value < num_pages:
            current_page.set(current_page.value + 1)

    def last():
        current_page.set(num_pages)

    def first():
        current_page.set(1)

    with solara.Row(justify="space-between"):
        solara.Button(
            "First",
            on_click=first,
            disabled=current_page.value == 1,
            classes=["button"],
        )
        solara.Button(
            "Previous Page",
            on_click=previous,
            disabled=current_page.value == 1,
            classes=["button"],
        )
        solara.Text(f"Current Page: {current_page.value} of {num_pages}")
        solara.Text(f"Total: {num_items}")
        solara.Button(
            "Next Page",
            on_click=next,
            classes=["button"],
            disabled=(current_page.value == num_pages) or num_pages == 0,
        )
        solara.Button(
            "Last",
            on_click=last,
            classes=["button"],
            disabled=(current_page.value == num_pages) or num_pages == 0,
        )
