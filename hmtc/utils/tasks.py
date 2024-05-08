import time


def long_task2(x):
    print("Task started")
    with open("output.txt", "w") as f:
        f.write("Task started")
        time.sleep(x)
        f.write("Task finished")

    return "Yay", 200
