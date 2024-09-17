from loguru import logger


class State:
    @classmethod
    def on_new(cls, item):
        logger.debug(f"🤡🤡BaseState🤡🤡 on_new: {item}, {item.__class__}")
        item.save_to_db()
        cls.refresh_query()

    @classmethod
    def on_delete(cls, item):
        logger.debug(f"🤡🤡BaseState🤡🤡 on_delete: {item}, {item.__class__}")
        db_item = item.grab_id_from_db(id=item.id)
        db_item.my_delete_instance()
        cls.refresh_query()

    @classmethod
    def on_update(cls, item):
        logger.debug(f"🤡🤡BaseState🤡🤡 on_update: {item}, {item.__class__}")
        assert item.title is not None
        item.save()
        cls.refresh_query()

    @classmethod
    def on_change_text_search(cls, text: str):
        logger.debug(f"🤡🤡BaseState🤡🤡 on_change_text_search: {text}")
        cls.text_query.value = text
        cls.refresh_query()

    @classmethod
    def on_page_change(cls, page: int):
        logger.debug(f"🤡🤡BaseState🤡🤡 on_page_change: {page}")
        cls.current_page.value = page
        cls.refresh_query()

    @classmethod
    def on_save(cls, item):
        logger.debug(f"🤡🤡BaseState🤡🤡 on_save: {item}")
        cls.on_new(item)
