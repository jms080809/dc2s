from typing import Callable
from datetime import datetime
import datetime as dt


def debug_print(function: Callable):
    def wrapper(*args, **kwargs):
        before = datetime.now()
        print(f"\033[34mExecuting {function.__name__} function...\033[0m")
        try:
            result = function(*args, **kwargs)
            after = datetime.now()
            print(f"\033[32mExecution of {function.__name__} was successful, took {(after-before).total_seconds()}s\033[0m")
            return result
        except Exception as e:
            print(f"\u001b[31mError: {e}\u001b[0m")
            raise

    return wrapper


def format_datetime(dt_obj: dt.datetime):
    year = dt_obj.year % 100
    month = dt_obj.month
    day = dt_obj.day
    hour_24 = dt_obj.hour
    minute = dt_obj.minute
    if hour_24 < 12:
        period = "AM"
        hour_12 = hour_24 if hour_24 != 0 else 12
    else:
        period = "PM"
        hour_12 = hour_24 - 12 if hour_24 > 12 else 12
    return f"{year}. {month}. {day}. {period} {hour_12}:{minute:02d}"


def attachment_align(attachment):
    url = attachment["url"]
    content_type = attachment["content_type"]
    return {"url": url, "content_type": content_type}
