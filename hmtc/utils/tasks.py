import time
from loguru import logger


def long_task2(x):
    print("Task started")
    logger.error(f"💥💥💥💥💥💥DELETE ME (6/9/24) 💥💥💥💥💥💥")
    with open("output.txt", "w") as f:
        f.write("Task started")
        time.sleep(x)
        f.write("Task finished")

    return "Yay", 200
