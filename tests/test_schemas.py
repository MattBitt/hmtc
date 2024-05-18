from hmtc.schemas.channel import ChannelItem
from hmtc.schemas.todo import TodoItem


def test_todo_schema():
    t = TodoItem(text="test", done=True, id=1)
    assert t.text == "test"
    assert t.done == True
    assert t.id == 1

    t = TodoItem.grab_id_from_db(1)
    assert t is None

    t = TodoItem(text="test", done=True)
    t.save_to_db()
    t = TodoItem.grab_id_from_db(1)
    assert t.text == "test"
    assert t.done == True
    assert t.id == 1

    t.text = "New Text"
    t.save()

    t = TodoItem.grab_id_from_db(1)
    assert t.text == "New Text"
    t.my_delete_instance()
    t = TodoItem.grab_id_from_db(1)
    assert t is None


def test_channel_schema():
    c = ChannelItem(name="asdf")
