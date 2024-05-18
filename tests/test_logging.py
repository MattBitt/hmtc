from loguru import logger


def greet(name):
    logger.info(f"Hello, {name}!")


def test_greet_logs_correct_message(caplog):
    greet("Alice")
    assert "Hello, Alice!" in caplog.text
