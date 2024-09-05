from typing import Dict

import solara
import solara.lab
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("../components/shared/carousel.vue")
def Carousel(children=[]):
    pass


@solara.component_vue("sandbox.vue")
def Sandbox(comp1="asdf", comp2="qwer", children=[]):
    pass


@solara.component
def SectionCard(section):
    with solara.Card():
        solara.Markdown(f"## Section Title {section}"),
        solara.Markdown(f"##### Section Content {section} asdf"),
        solara.Button(
            label="",
            icon_name="edit",
            on_click=lambda: logger.info(f"Clicked on {section}"),
            classes=["button"],
        ),


@solara.component
def Page():
    sections = solara.use_reactive(["a", "b", "c"])

    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        with Carousel():
            solara.Markdown("### Hello")
            solara.Markdown("#### World")
            solara.Markdown("##### Are you there")
            for sect in sections.value:
                SectionCard(section=sect)

        # with solara.Card():
        #     solara.Button(
        #         "Add Section", on_click=lambda: sections.set(sections.value + ["d"])
        #     )


# @solara.component
# def CounterDisplay(counter):
#     solara.Info(f"Counter: {counter.value}")


# @solara.component
# def IncrementButton(counter):

#     def increment():
#         counter.set(counter.value + [1])

#     solara.Button("Increment", on_click=increment)


# @solara.component
# def ItemAdder(items):

#     def add_item():
#         items.set(items.value + [items.value[-1] + 1])

#     solara.Button("Add Item", on_click=add_item)


# @solara.component
# def ItemList(items):
#     with solara.Columns():
#         for item in items.value:
#             solara.Button(
#                 f"Section #{item}",
#                 on_click=lambda: logger.info(f"Clicked on item {item}"),
#                 classes=["button"],
#             )


# @solara.component
# def Page():
#     items = solara.reactive([1, 2, 3])
#     counter = solara.reactive([1])
#     active_item = solara.reactive(1)
#     MySidebar(router=solara.use_router())

#     with solara.Column(classes=["main-container"]):
#         solara.Markdown("## Sandbox")
#         with solara.Card():
#             IncrementButton(counter=counter)
#             CounterDisplay(counter)
#             ItemAdder(items=items)
#             ItemList(items=items)
