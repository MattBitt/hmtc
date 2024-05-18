import dataclasses

from loguru import logger

from hmtc.models import TodoTable


# our model for a todo item, immutable/frozen avoids common bugs
@dataclasses.dataclass(frozen=True)
class TodoItem:

    text: str
    done: bool
    id: int = None

    @classmethod
    def grab_n_from_db(cls, n: int = 10):
        items = TodoTable.select().order_by(TodoTable.created_at.asc()).limit(n)
        return [TodoItem(text=item.text, done=item.done, id=item.id) for item in items]

    @classmethod
    def grab_id_from_db(cls, id: int):
        item = TodoTable.get_or_none(TodoTable.id == id)
        return item

    def from_dbmodel(self):
        if self.id is None:
            logger.error("Model not loaded from db yet.")
            return None
        model = TodoTable.get_by_id(self.id)
        return TodoItem(text=model.text, done=model.done, id=model.id)

    def save_to_db(self):
        logger.debug(f"Saving to db: {self}")
        if self.id is None:
            TodoTable.create(text=self.text, done=self.done)
        else:
            TodoTable.update(text=self.text, done=self.done).where(
                TodoTable.id == self.id
            ).execute()

    def delete_from_db(self):
        logger.debug(f"Deleting from db: {self}")
        TodoTable.delete().where(TodoTable.id == self.id).execute()
