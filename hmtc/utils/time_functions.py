import time
from datetime import datetime, timedelta


def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def time_ago_string(dt):
    time_ago = datetime.now().date() - dt

    if time_ago.days == 0:
        return "Today"
    if time_ago.days < 30:
        if time_ago.days == 1:
            return "Yesterday"
        else:
            return f"{time_ago.days} days ago"
    if time_ago.days < 365:
        months = time_ago.days // 30
        if months == 1:
            return "Last month"
        else:
            return f"{months} months ago"
    years = time_ago.days // 365
    if years == 1:
        return "Last year"
    else:
        return f"{years} years ago"
