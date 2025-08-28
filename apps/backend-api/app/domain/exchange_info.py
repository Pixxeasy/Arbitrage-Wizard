from typing import List

running_times: List[int] = []
average_time: float = 0
total_times: List[int] = []


def add_time(running_time: int):
    global running_times
    global average_time
    running_times.append(running_time)
    s_times = sum(running_times)
    average_time = s_times / len(running_times)


def add_total_time(total_time: int):
    global total_times
    total_times.append(total_time)


def get_relaxed_time():
    global average_time

    return average_time * 1.5


def get_last_total_time(count: int):
    global total_times
    if count > len(total_times):
        return None
    return total_times[-count]
