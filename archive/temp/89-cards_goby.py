from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.schemas.todo import TodoItem


@solara.component
def TodoEdit(
    todo_item: solara.Reactive[TodoItem],
    on_save: Callable[[], None],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    """Takes a reactive todo item and allows editing it. Will not modify the original item until 'save' is clicked."""
    copy = solara.use_reactive(todo_item.value)

    def save():
        todo_item.value = copy.value
        on_save()

    logger.debug("Start of TodoEdit")
    with solara.Card("Edit"):
        solara.InputText(label="TodoText", value=Ref(copy.fields.text))
        solara.Checkbox(label="Completed", value=Ref(copy.fields.done))
        with solara.CardActions():
            v.Spacer()
            solara.Button(
                "Save",
                icon_name="mdi-content-save",
                on_click=save,
                outlined=True,
                text=True,
            )
            solara.Button(
                "Close",
                icon_name="mdi-window-close",
                on_click=on_close,
                outlined=True,
                text=True,
            )
            solara.Button(
                "Delete",
                icon_name="mdi-delete",
                on_click=on_delete,
                outlined=True,
                text=True,
            )
    logger.debug("End of TodoEdit")


@solara.component
def TodoListItem(
    todo_item: solara.Reactive[TodoItem],
    on_update: Callable[[TodoItem], None],
    on_delete: Callable[[TodoItem], None],
):
    """Displays a single todo item, modifications are done 'in place'.

    For demonstration purposes, we allow editing the item in a dialog as well.
    This will not modify the original item until 'save' is clicked.
    """
    edit, set_edit = solara.use_state(False)
    with v.ListItem():

        solara.InputText(f"ID: {todo_item.value.id}", disabled=True)
        solara.InputText(label="", value=Ref(todo_item.fields.text), disabled=True)
        # solara.Markdown(todo_item.value.text)
        solara.Button(
            icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
        )
        solara.Button(
            icon_name="mdi-delete",
            icon=True,
            on_click=lambda: on_delete(todo_item.value),
        )
        with v.Dialog(
            v_model=edit, persistent=True, max_width="500px", on_v_model=set_edit
        ):
            if edit:  # 'reset' the component state on open/close

                def on_delete_in_edit():
                    on_delete(todo_item.value)
                    set_edit(False)

                def on_save_in_edit():
                    logger.debug(f"on_save_in_edit: {todo_item.value}")
                    on_update(todo_item.value)
                    set_edit(False)

                TodoEdit(
                    todo_item,
                    on_save=on_save_in_edit,
                    on_delete=on_delete_in_edit,
                    on_close=lambda: set_edit(False),
                )


@solara.component
def TodoNewTextBox(on_new: Callable[[TodoItem], None]):
    """Component that managed entering new todo items"""
    new_text, set_new_text = solara.use_state("")
    text_field = v.TextField(
        v_model=new_text, on_v_model=set_new_text, label="Enter a new todo item"
    )

    def create_new_item(*ignore_args):
        if not new_text:
            return
        new_item = TodoItem(text=new_text, done=False)
        on_new(new_item)
        # reset text
        set_new_text("")

    v.use_event(text_field, "keydown.enter", create_new_item)
    return text_field


@solara.component
def TodoNewButton(on_new: Callable[[TodoItem], None]):

    def create_new_item(*ignore_args):
        new_item = TodoItem(text="Buy Milk (default)", done=False)
        on_new(new_item)

    solara.Button("Create new ToDo Item (Default Text)", on_click=create_new_item)


# We store out reactive state, and our logic in a class for organization
# purposes, but this is not required.
# Note that all the above components do not refer to this class, but only
# to do the Todo items.
# This means all above components are reusable, and can be used in other
# places, while the components below use 'application'/'global' state.
# They are not suited for reuse.


class State:

    initial_items = TodoItem.grab_n_from_db(n=10)
    todos = solara.reactive(initial_items)

    @staticmethod
    def on_new(item: TodoItem):
        logger.debug(f"on_new: {item}, {item.__class__}")
        logger.info(f"Adding new item: {item}")
        item.save_to_db()
        State.todos.value = TodoItem.grab_n_from_db(n=10)

    @staticmethod
    def on_delete(item: TodoItem):
        logger.debug(f"on_delete: {item}, {item.__class__}")
        logger.info(f"Deleting item: {item}")
        db_item = item.grab_id_from_db(id=item.id)
        db_item.my_delete_instance()
        State.todos.value = TodoItem.grab_n_from_db(n=10)

    @staticmethod
    def on_update(item: TodoItem):
        logger.debug(f"on_update: {item}, {item.__class__}")
        logger.info(f"Updating existing item: {item}")
        item.save_to_db()
        State.todos.value = TodoItem.grab_n_from_db(n=10)


@solara.component
def TodoStatus():
    """Status of our todo list"""
    items = State.todos.value
    count = len(items)
    items_done = [item for item in items if item.done]
    count_done = len(items_done)

    if count != count_done:
        with solara.Row():
            percent = count_done / count * 100
            solara.ProgressLinear(value=percent)
        with solara.Row():
            solara.Text(f"Remaining: {count - count_done}")
            solara.Text(f"Completed: {count_done}")
    else:
        solara.Success("All done, awesome!", dense=True)


@solara.component
def Page():
    with solara.Card("Todo list", style="min-width: 500px"):
        TodoNewTextBox(on_new=State.on_new)
        if State.todos.value:
            TodoStatus()
            with solara.ColumnsResponsive(4):
                for index, item in enumerate(State.todos.value):
                    todo_item = Ref(State.todos.fields[index])
                    with solara.Card():
                        TodoListItem(
                            todo_item,
                            on_update=State.on_update,
                            on_delete=State.on_delete,
                        )
        else:
            solara.Info("No todo items, enter some text above, and hit enter")
        TodoNewButton(on_new=State.on_new)
