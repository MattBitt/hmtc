import solara
import ipyvuetify as v
import traitlets
import random


other_fruits = ["Pineapple", "Kiwi", "Cherry"]


class FruitSelector(v.VuetifyTemplate):
    template_file = "hmtc/pages/fruit-selector.vue"

    fruits = traitlets.List(traitlets.Unicode(), default_value=["Apple", "Pear"]).tag(
        sync=True
    )
    selected = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    can_add_from_python = traitlets.Bool(default_value=True).tag(sync=True)

    def vue_add_fruit_python(self, data=None):
        if other_fruits:
            fruit = other_fruits.pop()
            self.fruits = self.fruits + [fruit]
        if not other_fruits:
            self.can_add_from_python = False


@solara.component()
def Page():
    f = FruitSelector()
    f
