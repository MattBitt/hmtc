from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger
from solara.lab import task
from solara.lab.toestand import Ref

from hmtc.schemas.channel import ChannelItem


@solara.component
def ChannelEditModal(
    channel_item: solara.Reactive[ChannelItem],
    on_save: Callable[[], None],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    updating = solara.use_reactive(False)

    """Takes a reactive channel item and allows editing it. Will not modify the original item until 'save' is clicked."""
    copy = solara.use_reactive(channel_item.value)

    def save():
        channel_item.value = copy.value
        on_save()

    def update_playlists():
        logger.debug(f"Updating channel {channel_item.value.name}")
        updating.set(True)
        channel_item.value.db_object().check_for_new_playlists()
        updating.set(False)
        logger.success(f"Updated database from Channel {channel_item.value.name}")

    @task
    def update():
        logger.debug(f"Updating channel {channel_item.value.name}")
        updating.set(True)
        channel_item.value.db_object().check_for_new_videos()
        updating.set(False)
        logger.success(f"Updated database from Channel {channel_item.value.name}")

    logger.debug("Start of ChannelEdit")
    with solara.Card("Edit"):
        solara.InputText(label="ID", value=Ref(copy.fields.id), disabled=True)
        solara.InputText(label="Channel Name", value=Ref(copy.fields.name))
        solara.InputText(label="URL", value=Ref(copy.fields.url))
        solara.InputText(label="YouTube ID", value=Ref(copy.fields.youtube_id))
        solara.Checkbox(label="Enabled", value=Ref(copy.fields.enabled))

        if channel_item.value is not None:
            solara.Image(channel_item.value.db_object().poster, width="300px")

        solara.Button(label="Check for new Videos", on_click=update)
        solara.Button(label="Check for new Playlists", on_click=update_playlists)

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


@solara.component
def ChannelListItem(
    channel_item: solara.Reactive[ChannelItem],
    on_update: Callable[[ChannelItem], None],
    on_delete: Callable[[ChannelItem], None],
):
    """Displays a single channel item, modifications are done 'in place'.

    For demonstration purposes, we allow editing the item in a dialog as well.
    This will not modify the original item until 'save' is clicked.
    """
    edit, set_edit = solara.use_state(False)
    with v.ListItem():

        solara.InputText(f"ID: {channel_item.value.id}", disabled=True)
        solara.InputText(label="", value=Ref(channel_item.fields.name), disabled=True)
        # solara.Markdown(channel_item.value.text)
        solara.Button(
            icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
        )
        solara.Button(
            icon_name="mdi-delete",
            icon=True,
            on_click=lambda: on_delete(channel_item.value),
        )
        with v.Dialog(
            v_model=edit, persistent=True, max_width="500px", on_v_model=set_edit
        ):
            if edit:  # 'reset' the component state on open/close

                def on_delete_in_edit():
                    on_delete(channel_item.value)
                    set_edit(False)

                def on_save_in_edit():
                    logger.debug(f"on_save_in_edit: {channel_item.value}")
                    on_update(channel_item.value)
                    set_edit(False)

                ChannelEditModal(
                    channel_item,
                    on_save=on_save_in_edit,
                    on_delete=on_delete_in_edit,
                    on_close=lambda: set_edit(False),
                )


@solara.component
def ChannelNewTextBox(on_new: Callable[[ChannelItem], None]):
    """Component that managed entering new channel items"""
    new_text, set_new_text = solara.use_state("")
    text_field = v.TextField(
        v_model=new_text, on_v_model=set_new_text, label="Enter a new channel item"
    )

    def create_new_item(*ignore_args):
        if not new_text:
            return
        new_item = ChannelItem(name=new_text, done=False)
        on_new(new_item)
        # reset text
        set_new_text("")

    v.use_event(text_field, "keydown.enter", create_new_item)
    return text_field


@solara.component
def ChannelNewButton(on_new: Callable[[ChannelItem], None]):

    def create_new_item(*ignore_args):
        new_item = ChannelItem(
            name="Some Youtube Channel", enabled=True, youtube_id="1234"
        )
        on_new(new_item)

    solara.Button("Create new Channel Item (Default Text)", on_click=create_new_item)


# We store out reactive state, and our logic in a class for organization
# purposes, but this is not required.
# Note that all the above components do not refer to this class, but only
# to do the Channel items.
# This means all above components are reusable, and can be used in other
# places, while the components below use 'application'/'global' state.
# They are not suited for reuse.


class State:

    initial_items = ChannelItem.grab_n_from_db(n=10)
    channels = solara.reactive(initial_items)

    @staticmethod
    def on_new(item: ChannelItem):
        logger.debug(f"on_new: {item}, {item.__class__}")
        logger.info(f"Adding new item: {item}")
        item.save_to_db()
        State.channels.value = ChannelItem.grab_n_from_db(n=10)

    @staticmethod
    def on_delete(item: ChannelItem):
        logger.debug(f"on_delete: {item}, {item.__class__}")
        logger.info(f"Deleting item: {item}")
        db_item = item.grab_id_from_db(id=item.id)
        db_item.my_delete_instance()
        State.channels.value = ChannelItem.grab_n_from_db(n=10)

    @staticmethod
    def on_update(item: ChannelItem):
        logger.debug(f"on_update: {item}, {item.__class__}")
        logger.info(f"Updating existing item: {item}")
        item.save_to_db()
        State.channels.value = ChannelItem.grab_n_from_db(n=10)


@solara.component
def ChannelStatus():
    """Status of our channel list"""
    items = State.channels.value
    count = len(items)
    items_done = [item for item in items if item.enabled]
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
    with solara.Card("Channel list", style="min-width: 80%"):
        ChannelNewTextBox(on_new=State.on_new)
        if State.channels.value:
            ChannelStatus()
            with solara.ColumnsResponsive(4):
                for index, item in enumerate(State.channels.value):
                    channel_item = Ref(State.channels.fields[index])
                    with solara.Card():
                        ChannelListItem(
                            channel_item,
                            on_update=State.on_update,
                            on_delete=State.on_delete,
                        )
        else:
            solara.Info("No channel items, enter some text above, and hit enter")
        ChannelNewButton(on_new=State.on_new)
