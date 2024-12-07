from loguru import logger


def myhandler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Handle the exception here
            logger.error(f"An error occurred in {func.__name__}: {e}")
            raise e

    return wrapper


@myhandler
def divide_numbers(a, b):
    return a / b


if __name__ == "__main__":
    result = divide_numbers(10, 0)
    print(result)
